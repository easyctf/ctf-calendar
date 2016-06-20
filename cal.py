import os

from flask import Flask

import config
import views
from filters import filters
from models import db, login_manager

app = Flask(__name__, static_url_path='')
self_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_object(config.CalendarConfig(app_root=self_path))
db.init_app(app)

login_manager.init_app(app)

app.register_blueprint(views.base.blueprint)
app.register_blueprint(views.events.blueprint, url_prefix='/events')
app.register_blueprint(views.users.blueprint)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

for name, func in filters.items():
    app.add_template_filter(func, name=name)
