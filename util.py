import datetime
import os
import random
import re
import time
from functools import wraps, update_wrapper

from flask import abort
from flask_login import current_user, login_required
from passlib.hash import bcrypt
from redis import from_url

redis = from_url(os.getenv("REDIS_URL"))


def cache(expire_in=120, uid=None):
    def decorator(f):
        def cache_function(*args, **kwargs):
            arg_collection = list(args) + sorted(kwargs.items())
            key = 'cache/%s/%s' % (f.__name__, arg_collection)
            if uid is not None:
                key = '%s/%s' % (key, uid())
            with redis.pipeline() as p:
                p.get(key)
                result = p.execute()[0]
                if result is None:
                    result = f(*args, **kwargs)
                    p.set(key, result)
                    p.expireat(key, int(time.time() + expire_in))
                    p.execute()
            return result

        return update_wrapper(cache_function, f)

    return decorator


def uncache(function_name=None, args=None, uid=None):
    if not function_name: return
    key = 'cache/%s/%s' % (function_name, args)
    if uid is not None:
        key = '%s/%s' % (key, uid)
    with redis.pipeline() as p:
        p.delete(key)
        p.execute()


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
