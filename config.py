import os

import pathlib
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

EVENT_LIST_PAGE_SIZE = 25
USER_LIST_PAGE_SIZE = 50


class CalendarConfig:
    def __init__(self, app_root=None, testing=False):
        if app_root is None:
            self.app_root = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.app_root = pathlib.Path(app_root)

        self.SECRET_KEY = None
        self._load_secret_key()
        self.SQLALCHEMY_DATABASE_URI = self._get_database_url()
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.TEMPLATES_AUTO_RELOAD = True

        self.MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN', '')
        self.MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY', '')

        if testing:
            self.DEBUG = True
            self.TESTING = True
            self.WTF_CSRF_ENABLED = False

    def _load_secret_key(self):
        if 'SECRET_KEY' in os.environ:
            self.SECRET_KEY = os.environ['SECRET_KEY']
        else:
            secret_path = self.app_root / '.secret_key'
            with secret_path.open('rb') as secret_file:
                secret_file.seek(0)
                contents = secret_file.read()
                if not contents and len(contents) == 0:
                    key = os.urandom(128)
                    secret_file.write(key)
                    secret_file.flush()
                else:
                    key = contents
            self.SECRET_KEY = key

        return self.SECRET_KEY

    def _get_database_url(self):
        return os.getenv('DATABASE_URL', '')
