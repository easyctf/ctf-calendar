from passlib.hash import bcrypt
import re


def hash_password(password, rounds=10):
    return bcrypt.encrypt(password, rounds=rounds)


def verify_password(to_check, password_hash):
    return bcrypt.verify(to_check, password_hash)


def validate_email_format(email):
    return re.match('[^@]+@[^@]+\.[^@]+', email) is not None


def validate_username_format(username):
    return re.match('^[a-zA-Z0-9_.-\[\]\(\)]+$', username) is not None