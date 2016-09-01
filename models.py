from datetime import datetime, timedelta
from functools import partial

from flask_login import current_user, LoginManager
from flask_oauthlib.provider import OAuth2Provider
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref

import util

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth2Provider()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(length=128), unique=True)
    email = db.Column(db.Unicode(length=128), unique=True)
    _password = db.Column('password', db.String(length=60))  # password hash
    admin = db.Column(db.Boolean, default=False)
    joined = db.Column(db.DateTime, default=datetime.utcnow)

    def __eq__(self, other):
        if isinstance(other, User):
            return self.id == other.id
        return NotImplemented

    '''Python 3 implicitly sets __hash__ to None if __eq__ is overridden. Set back to default implementation.'''

    def __hash__(self):
        return object.__hash__(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @classmethod
    def get_by_id(cls, id):
        query_results = cls.query.filter_by(id=id)
        return query_results.first() if query_results.count() else None

    @staticmethod
    @login_manager.user_loader
    def get_user_by_id(id):
        return User.get_by_id(id)

    @classmethod
    def get_by_identifier(cls, identifier):
        if '@' in identifier:  # identifier is email
            query_results = cls.query.filter_by(email=identifier)
        else:  # identifier is username
            query_results = cls.query.filter_by(username=identifier)
        return query_results.first() if query_results.count() else None

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = util.hash_password(password)

    def check_password(self, password):
        return util.verify_password(password, self.password)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', name='event_owner_id_fk'))
    owner = db.relationship('User', backref=backref('events', lazy='dynamic'))
    approved = db.Column(db.Boolean, default=False)
    title = db.Column(db.Unicode(length=256))
    start_time = db.Column(db.Integer, index=True)
    duration = db.Column(db.Float)  # in hours
    description = db.Column(db.UnicodeText)
    link = db.Column(db.Unicode(length=256))
    removed = db.Column(db.Boolean, default=False)

    # OAuth2 stuff
    client_id = db.Column(db.String(40), unique=True, default=partial(util.generate_string, 16))
    client_secret = db.Column(db.String(55), unique=True, index=True, nullable=False, default=partial(util.generate_string, 32))
    is_confidential = db.Column(db.Boolean, default=True)
    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def formatted_start_time(self):
        return util.isoformat(self.start_time)

    @hybrid_property
    def end_time(self):
        return self.start_time + self.duration * 60

    @property
    def formatted_end_time(self):
        return util.isoformat(self.end_time)

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []


class EventVote(db.Model):
    __tablename__ = 'eventvotes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='eventvote_user_id_fk'))
    user = db.relationship('User', backref='event_votes')
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', name='vote_event_id_fk'), index=True)
    event = db.relationship('Event', backref='votes')
    direction = db.Column(db.Boolean)
    __table_args__ = (UniqueConstraint('user_id', 'event_id', name='eventvote_user_event_uc'),)


class Grant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')

    client_id = db.Column(db.String(40), db.ForeignKey('events.client_id'), nullable=False)
    client = db.relationship('Event')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('events.client_id'),
        nullable=False,
    )
    client = db.relationship('Event')

    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id')
    )
    user = db.relationship('User')

    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


def get_current_user():
    if current_user:
        return current_user
    return None


@oauth.clientgetter
def load_client(client_id):
    return Event.query.filter_by(client_id=client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=get_current_user(),
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = Token.query.filter_by(client_id=request.client.client_id,
                                 user_id=request.user.id)
    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

    expires_in = token.get('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok
