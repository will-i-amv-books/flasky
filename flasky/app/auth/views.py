from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user 

from app import db
from app.auth import auth
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm


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
        flash('You can now login.')
        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
