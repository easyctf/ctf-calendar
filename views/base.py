from flask import Blueprint, render_template

blueprint = Blueprint('base', __name__, template_folder='templates')


@blueprint.route("/")
def index():
    return render_template("base/index.html")

@blueprint.route("/about")
def about():
    return render_template("base/about.html")


@blueprint.app_errorhandler(404)
def error_404(e):
    return render_template('base/404.html'), 404
