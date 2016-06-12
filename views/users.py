from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user

from forms import LoginForm, RegisterForm
from models import db
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


@blueprint.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('users/profile.html', user=current_user)


@blueprint.route('/users')
def users_list():
    users = User.query.order_by(User.id).all()
    return render_template('users/list.html', users=users)


@blueprint.route('/users/<int:user_id>')
def users_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('users/profile.html', user=user)
