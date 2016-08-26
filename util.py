import datetime
import random
import re
from functools import wraps

from flask import abort
from flask_login import current_user, login_required
from passlib.hash import bcrypt


def isoformat(seconds):
    return datetime.datetime.fromtimestamp(seconds).isoformat() + "Z"


def generate_string(length=32, alpha='0123456789abcdef'):
    return "".join([random.choice(alpha) for x in range(length)])


def hash_password(password, rounds=10):
    return bcrypt.encrypt(password, rounds=rounds)


def verify_password(to_check, password_hash):
    return bcrypt.verify(to_check, password_hash)


def validate_email_format(email):
    return re.match('[^@]+@[^@]+\.[^@]+', email) is not None


def validate_username_format(username):
    return re.match('^[a-zA-Z0-9_.-\[\]\(\)]+$', username) is not None


def admin_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.admin:
            abort(403)
        return func(*args, **kwargs)

    return wrapper
