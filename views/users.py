from datetime import datetime, timedelta

import requests
from flask import abort, Blueprint, render_template, redirect, url_for, send_file, request
from flask import current_app as app
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func

import config
import util
from forms import LoginForm, RegisterForm, PasswordForgotForm, PasswordResetForm
from models import db, PasswordResetToken
from models import login_manager, User

login_manager.login_view = '/login'

blueprint = Blueprint('users', __name__, template_folder='templates')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        login_user(login_form.get_user())
        return redirect(
            url_for('.profile'))  # TODO: implement safe redirection based on url value for login and register
    return render_template('users/login.html', login_form=login_form)


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        new_user = User()
        register_form.populate_obj(new_user)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('.profile'))
    return render_template('users/register.html', register_form=register_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base.index'))


@blueprint.route('/avatar/<int:user_id>')
def user_avatar(user_id):
    user = User.query.get_or_404(user_id)
    return send_file('static/images/user.jpg')


@blueprint.route('/password/forgot', methods=['GET', 'POST'])
def user_password_forgot():
    forgot_form = PasswordForgotForm()
    if forgot_form.validate_on_submit():
        user = forgot_form.user
        if user is not None:
            token = PasswordResetToken.query.filter(
                (func.lower(PasswordResetToken.email) == forgot_form.email.data.lower()) &
                (PasswordResetToken.active is True)
            ).first()
            if token:
                token.token = util.generate_string(16)
                token.expire = datetime.now() + timedelta(days=1)
            else:
                token = PasswordResetToken(active=True, email=forgot_form.email.data,
                                           expire=datetime.now() + timedelta(days=1))
                db.session.add(token)
            db.session.commit()
            url = "http://%s/password/reset/%s" % (request.host, token.token)
            requests.post('https://api.mailgun.net/v3/%s/messages' % app.config['MAILGUN_DOMAIN'],
                          auth=('api', app.config['MAILGUN_API_KEY']), data={
                    "from": "CTF Calendar Admin <team@easyctf.com>",
                    "to": forgot_form.email.data,
                    "subject": "CTF Calendar Password Reset",
                    "html": "Click here to reset your password: <a href='%s'>%s</a>" % (url, url)
                })
        return render_template('users/forgot.html', check_your_email=True)
    return render_template('users/forgot.html', forgot_form=forgot_form)


@blueprint.route('/password/reset/<string:code>', methods=['GET', 'POST'])
def user_password_reset(code):
    reset_form = PasswordResetForm()
    if reset_form.validate_on_submit():
        token = PasswordResetToken.query.filter_by(token=reset_form.code.data).first()
        user = User.query.filter(func.lower(User.email) == token.email.lower()).first()
        user.password = reset_form.password.data
        token.active = False
        db.session.add(user)
        db.session.add(token)
        db.session.commit()
        return render_template('users/reset.html', password_reset=True)
    return render_template('users/reset.html', code=code, reset_form=reset_form)


@blueprint.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('users/profile.html', user=current_user)


@blueprint.route('/users')
@blueprint.route('/users/page/<int:page_number>')
def users_list(page_number=1):
    if page_number <= 0:
        abort(404)

    page_size = config.USER_LIST_PAGE_SIZE
    page_offset = (page_number - 1) * page_size
    users = User.query.order_by(User.id).order_by(User.id.desc()).offset(page_offset).limit(page_size + 1).all()
    if page_number != 1 and not users:
        abort(404)

    last_page = len(users) <= page_size
    if not last_page:
        users.pop()

    return render_template('users/list.html', page_number=page_number, last_page=last_page, users=users)


@blueprint.route('/users/<int:user_id>')
def users_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('users/profile.html', user=user)
