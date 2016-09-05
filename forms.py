from flask_wtf import Form
from sqlalchemy import func
from wtforms import ValidationError
from wtforms.fields import *
from wtforms.validators import *
from wtforms.widgets import TextArea

import util
from datetime import datetime
from models import User, PasswordResetToken


class LoginForm(Form):
    identifier = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

    def get_user(self, identifier=None):
        return User.get_by_identifier(identifier or self.identifier.data)

    def validate_identifier(self, field):
        if self.get_user(field.data) is None:
            raise ValidationError('Invalid identifier')

    def validate_password(self, field):
        user = self.get_user(self.identifier.data)
        if not user:
            return
        if not user.check_password(field.data):
            raise ValidationError('Invalid password')


class RegisterForm(Form):
    email = StringField('Email', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=16,
                                                                           message='Username must be between 4 and 16 characters long.')])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=56,
                                                                             message='Password must be between 8 and 56 characters long.')])

    def validate_email(self, field):
        if not util.validate_email_format(field.data):
            raise ValidationError('Invalid email')
        if User.query.filter(func.lower(User.email) == func.lower(field.data)).count():
            raise ValidationError('Email taken!')

    def validate_username(self, field):
        if not util.validate_username_format(field.data):
            raise ValidationError('Invalid username')
        if User.query.filter(func.lower(User.username) == func.lower(field.data)).count():
            raise ValidationError('Username taken!')


class PasswordForgotForm(Form):
    email = StringField('Email', validators=[InputRequired()])

    def __init__(self):
        super(PasswordForgotForm, self).__init__()
        self._user = None
        self._user_cached = False

    @property
    def user(self):
        if not self._user_cached:
            self._user = User.query.filter(func.lower(User.email) == func.lower(self.email.data)).first()
            self._user_cached = True
        return self._user

    def validate_email(self, field):
        if not util.validate_email_format(field.data):
            raise ValidationError('Invalid email')


class PasswordResetForm(Form):
    code = HiddenField('Code', validators=[InputRequired()])
    password = PasswordField('New Password', validators=[InputRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match.')])

    def validate_code(self, field):
        token = PasswordResetToken.query.filter_by(token=field.data, active=True).first()
        if not token or datetime.now() > token.expire:
            raise ValidationError('Invalid code')


class EventForm(Form):
    title = StringField('Title', validators=[InputRequired(), Length(max=256)])
    start_time = IntegerField('Start Time (UNIX Time)', validators=[InputRequired(), NumberRange(min=0, max=2147483647,
                                                                                                 message='Start time must be between 0 and 2147483647!')])
    duration = FloatField('Duration (Hours)', validators=[InputRequired(), NumberRange(min=0, max=2147483647,
                                                                                       message='Duration must be between 0 and 2147483647!')])
    description = StringField('Description', widget=TextArea(), validators=[InputRequired(), Length(max=1024)])
    link = StringField('Link', validators=[InputRequired(), Length(max=256)])

    def validate_link(self, field):
        if not any(field.data.startswith(prefix) for prefix in [u'http://', u'https://']):
            raise ValidationError('Invalid link')
