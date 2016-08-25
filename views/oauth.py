from flask import Blueprint, request, render_template
from flask_login import login_required

from models import oauth, Event

blueprint = Blueprint('oauth', __name__, template_folder='templates')


@blueprint.route('/authorize', methods=['GET', 'POST'])
@login_required
@oauth.authorize_handler
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Event.query.filter_by(client_id=client_id).first()
        kwargs['client'] = client
        return render_template('oauthorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'


@blueprint.route('/token')
@oauth.token_handler
def access_token():
    return None


@blueprint.route('/revoke', methods=['POST'])
@oauth.revoke_handler
def revoke_token(): pass
