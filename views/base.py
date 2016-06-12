from flask import Blueprint, render_template, url_for

blueprint_base = Blueprint('base', __name__, template_folder='templates')

@blueprint_base.route("/")
def index():
    return render_template("base/index.html")


@blueprint_base.app_errorhandler(404)
def error_404(e):
    return render_template('base/404.html'), 404
