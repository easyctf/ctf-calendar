import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

import config

app = Flask(__name__)
self_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_object(config.CalendarConfig(app_root=self_path))
db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template("index.html")
