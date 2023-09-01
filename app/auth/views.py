from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user 

from app import db
from app.email import send_email
from app.auth import auth
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm


@auth.before_app_request
def before_request():
    if (
        (current_user.is_authenticated) 
        and (not current_user.confirmed) 
        and (request.blueprint != 'auth') 
        and (request.endpoint != 'static')
    ):
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('auth/login.html', form=form)
    else:
        user = User.query.filter_by(email=form.email.data).first()
        if not (
            (user is not None) and 
            (user.verify_password(form.password.data))
        ):
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
        else:
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if (next is None) or (not next.startswith('/')):
                next = url_for('main.index')
            return redirect(next)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if not form.validate_on_submit():
        return render_template('auth/register.html', form=form)
    else:
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email, 
            'Confirm Your Account',
            'auth/email/confirm', 
            user=user,
            token=token
        )
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if (current_user.is_anonymous) or (current_user.confirmed):
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    elif current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email, 
        'Confirm Your Account',
        'auth/email/confirm', 
        user=current_user,
        token=token
    )
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
