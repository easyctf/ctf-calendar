from flask import Flask
from flask_runner import Runner
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)
runner = Runner(app)


@app.route("/")
def index():
	return "Hello World!"


if __name__ == "__main__":
	runner.run()
