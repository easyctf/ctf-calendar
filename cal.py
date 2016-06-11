import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import config
from models import db, login_manager

app = Flask(__name__)
self_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_object(config.CalendarConfig(app_root=self_path))

with app.app_context():
	db.init_app(app)
	db.create_all()
	app.db = db

login_manager.init_app(app)

from views import blueprint_base, blueprint_events, blueprint_users
app.register_blueprint(blueprint_base)
app.register_blueprint(blueprint_users)
app.register_blueprint(blueprint_events, url_prefix='/events')

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
