from flask import redirect, render_template, abort, url_for, flash, request
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from . forms import LoginForm, RegisterForm, ChangePwForm
from .. import db
from ..models import User, load_user
from ..emailq import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login',methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user is not None and user.passwordverify(form.password.data):
            login_user(user, form.remember.data)
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html',form=form)


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        flash('u should logout first')
        return redirect(url_for('main.index'))
    elif form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        db.session.commit()
        flash('Welcome to TodoList and a confirmed email has been sent to you')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The link is invalid')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(user.email, 'Confirm Your Account',
               'auth/email/confirm', user=user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change_pw', methods=['GET', 'POST'])
@login_required
def change_pw():
    form = ChangePwForm()
    if form.validate_on_submit():
        if current_user.passwordverify(form.old_pw.data):
            current_user.password = form.new_pw.data
            db.session.add(current_user)
            db.session.commit()
            logout_user()
            flash('Your password has been updated, and you need to log in again')
            return redirect(url_for('auth.login'))
        flash('Invalid password')
    return render_template("auth/change_pw.html",form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('u have logout.')
    return redirect(url_for('main.index'))