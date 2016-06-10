import os

from flask import Flask, render_template
from flask_runner import Runner
from flask_sqlalchemy import SQLAlchemy

import config

app = Flask(__name__)
self_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_object(config.CalendarConfig(app_root=self_path))
db = SQLAlchemy(app)


@app.route("/")
def index():
	return render_template("index.html")


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
