import os
import pathlib

class CalendarConfig:
    def __init__(self, app_root=None, testing=False):
        if app_root is None:
            self.app_root = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.app_root = pathlib.Path(app_root)

        self.SECRET_KEY = None
        self._load_secret_key()
        self.SQLALCHEMY_DATABASE_URI = self.get_mysql_url()    
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        if testing:
            self.TESTING = True
            self.WTF_CSRF_ENABLED = False

    def _load_secret_key(self):
        if not self.SECRET_KEY:
            secret_path = self.app_root / '.secret_key'
            with secret_path.open('a+b') as secret_file:
                contents = secret_file.read()
                if not contents:
                    key = os.urandom(128)
                    secret_file.write(key)
                    secret_file.flush()
                else:
                    key = contents
            self.SECRET_KEY = key

        return self.SECRET_KEY

    def get_mysql_url(self):
        password_path = self.app_root / 'MYSQL_SECRET'
        if password_path.is_file():
            with password_path.open('r') as password_file:
                password = password_file.read().strip()
        else:
            password = ''
        return password
