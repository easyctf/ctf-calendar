from flask import Blueprint, request, jsonify

from models import oauth

blueprint = Blueprint('api', __name__)


@blueprint.route('/me')
@oauth.require_oauth('user')
def me():
    user = request.oauth.user
    return jsonify(email=user.email, username=user.username, id=user.id)
