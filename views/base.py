from flask import Blueprint, render_template

from models import Event

blueprint = Blueprint('base', __name__, template_folder='templates')


@blueprint.route('/')
def index():
    events = Event.query.filter_by(approved=True, removed=False).order_by(Event.start_time.desc()).all()
    return render_template('base/index.html', events=events)


@blueprint.route('/about')
def about():
    return render_template('base/about.html')


@blueprint.app_errorhandler(404)
def error_404(e):
    return render_template('base/404.html'), 404
