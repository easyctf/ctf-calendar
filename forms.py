from flask_wtf import Form
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import InputRequired, Length

from models import User
import util


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
    username = StringField('Username', validators=[InputRequired(), Length(min=4)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])

    def validate_email(self, field):
        if not util.validate_email_format(field.data):
            raise ValidationError('Invalid email')

    def validate_username(self, field):
        if not util.validate_username_format(field.data):
            raise ValidationError('Invalid username')