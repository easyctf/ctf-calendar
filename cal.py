import os

from flask import Flask

import config
from models import db, login_manager
from views import blueprint_base, blueprint_events, blueprint_users

app = Flask(__name__, static_url_path='')
self_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_object(config.CalendarConfig(app_root=self_path))
db.init_app(app)

login_manager.init_app(app)

app.register_blueprint(blueprint_base)
app.register_blueprint(blueprint_users)
app.register_blueprint(blueprint_events, url_prefix='/events')

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
