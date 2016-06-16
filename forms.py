from datetime import datetime

from flask_wtf import Form
from sqlalchemy import func
from wtforms import ValidationError
from wtforms.fields import *
from wtforms.validators import InputRequired, Length
from wtforms.widgets import TextArea

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
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=128)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=56)])

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


class EventForm(Form):
    title = StringField('Title', validators=[InputRequired(), Length(max=256)])
    start_time = IntegerField('Start Time', validators=[InputRequired()])
    duration = FloatField('Duration (hours)', validators=[InputRequired()])
    description = StringField('Description', widget=TextArea(), validators=[InputRequired(), Length(max=1024)])
    link = StringField('Link', validators=[InputRequired(), Length(max=256)])

    def validate_link(self, field):
        if not any(field.data.startswith(prefix) for prefix in [u'http://', u'https://']):
            raise ValidationError('Invalid link')
