from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from cal import db
from forms import LoginForm, RegisterForm
from models import login_manager, User

blueprint_base = Blueprint('base', __name__, template_folder='templates')
blueprint_users = Blueprint('users', __name__, template_folder='templates')


@blueprint_base.route("/")
def index():
    return render_template("base/index.html")


@blueprint_users.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        login_user(login_form.get_user())
        return redirect(
            url_for('.profile'))  # TODO: implement safe redirection based on url value for login and register
    return render_template('users/login.html', login_form=login_form)


login_manager.login_view = '/login'


@blueprint_users.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        new_user = User(email=register_form.email.data,
                        username=register_form.username.data,
                        password=register_form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('.profile'))
    return render_template('users/register.html', register_form=register_form)


@blueprint_users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base.index'))


@blueprint_users.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('users/profile.html')
