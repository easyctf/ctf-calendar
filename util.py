import datetime
import os
import random
import re
import time
from functools import wraps, update_wrapper

from flask import abort
from flask import g
from flask_login import current_user, login_required
from passlib.hash import bcrypt
from redis import from_url

redis = from_url(os.getenv("REDIS_URL"))


class RateLimitedException(Exception): pass


class RateLimit(object):
    expiration_window = 10

    def __init__(self, key_prefix, limit, interval, send_x_headers):
        self.reset = (int(time.time()) // interval) * interval + interval
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.interval = interval
        self.send_x_headers = send_x_headers
        with redis.pipeline() as p:
            p.incr(self.key)
            p.expireat(self.key, self.reset + self.expiration_window)
            self.current = p.execute()[0]  # min(p.execute()[0], limit)

    def increment(self):
        with redis.pipeline() as p:
            p.incr(self.key)

    def decrement(self):
        with redis.pipeline() as p:
            p.decr(self.key)

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current > x.limit)


def rate_limit(limit=1, interval=120, send_x_headers=True, scope_func='global'):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'ratelimit/%s/%s/' % (f.__name__, scope_func())
            rlimit = RateLimit(key, limit, interval, send_x_headers)
            g._view_rate_limit = rlimit
            if rlimit.over_limit:
                raise RateLimitedException("You done fucked.")
            try:
                result = f(*args, **kwargs)
            except Exception, e:
                rlimit.decrement()
            return result

        return update_wrapper(rate_limited, f)

    return decorator


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
