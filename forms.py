from flask_wtf import Form
from sqlalchemy import func
from wtforms import ValidationError
from wtforms.fields import *
from wtforms.validators import *
from wtforms.widgets import TextArea
from wtforms_components import read_only

import util
from models import User


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


class EventCreateForm(Form):
    title = StringField('Title', validators=[InputRequired(), Length(max=256)])
    start_time = IntegerField('Start Time', validators=[InputRequired(), NumberRange(min=0, max=2147483647,
                                                                                     message='Start time must be between 0 and 2147483647!')])
    duration = FloatField('Duration (hours)', validators=[InputRequired(), NumberRange(min=0, max=2147483647,
                                                                                       message='Duration must be between 0 and 2147483647!')])
    description = StringField('Description', widget=TextArea(), validators=[InputRequired(), Length(max=1024)])
    link = StringField('Link', validators=[InputRequired(), Length(max=256)])

    def validate_link(self, field):
        if not any(field.data.startswith(prefix) for prefix in [u'http://', u'https://']):
            raise ValidationError('Invalid link')


class EventManageForm(Form):
    title = StringField('Title', validators=[InputRequired(), Length(max=256)])
    start_time = IntegerField('Start Time', validators=[InputRequired(), NumberRange(min=0, max=2147483647,
                                                                                     message='Start time must be between 0 and 2147483647!')])
    duration = FloatField('Duration (hours)', validators=[InputRequired(), NumberRange(min=0, max=2147483647,
                                                                                       message='Duration must be between 0 and 2147483647!')])
    description = StringField('Description', widget=TextArea(), validators=[InputRequired(), Length(max=1024)])
    link = StringField('Link', validators=[InputRequired(), Length(max=256)])
    client_id = StringField('Client ID')
    client_secret = StringField('Client Secret')
    redirect_uris = StringField('Redirect URIs', widget=TextArea(), validators=[])

    def __init__(self, *args, **kwargs):
        super(EventManageForm, self).__init__(*args, **kwargs)
        read_only(self.client_id)
        read_only(self.client_secret)

    def validate_link(self, field):
        if not any(field.data.startswith(prefix) for prefix in [u'http://', u'https://']):
            raise ValidationError('Invalid link')
