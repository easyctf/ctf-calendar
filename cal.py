import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

import config
from models import db, login_manager
from views import blueprint

app = Flask(__name__)
self_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_object(config.CalendarConfig(app_root=self_path))
db.init_app(app)
login_manager.init_app(app)
app.register_blueprint(blueprint)
