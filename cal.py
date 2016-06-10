import os

from flask import Flask
from flask_runner import Runner
from flask_sqlalchemy import SQLAlchemy

import config

app = Flask(__name__)
self_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_object(config.CalendarConfig(app_root=self_path))
db = SQLAlchemy(app)
runner = Runner(app)


@app.route("/")
def index():
	return "Hello World!"


if __name__ == "__main__":
	runner.run()
