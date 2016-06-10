from flask import Flask
from flask_runner import Runner

app = Flask(__name__)
runner = Runner(app)

@app.route("/")
def index():
	return "Hello World!"

if __name__ == "__main__":
	runner.run()