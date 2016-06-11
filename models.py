from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

import util

db = SQLAlchemy()
login_manager = LoginManager()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(length=128), unique=True)
    email = db.Column(db.Unicode(length=128), unique=True)
    _password = db.Column('password', db.String(length=60))  # password hash
    admin = db.Column(db.Boolean, default=False)

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
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = db.relationship('User', backref='events')
    approved = db.Column(db.Boolean, default=False)
    title = db.Column(db.Unicode(length=256))
    start_time = db.Column(db.DateTime, index=True)
    duration = db.Column(db.Float)
    description = db.Column(db.UnicodeText)
    link = db.Column(db.Unicode(length=256))


class EventVote(db.Model):
    __tablename__ = 'eventvotes'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), index=True)
    event = db.relationship('Event', backref='votes')
    direction = db.Column(db.Boolean)
