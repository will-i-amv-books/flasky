from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user

from . import auth
from ..models import User
from .forms import LoginForm


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
            next = (
                request.args.get('next')
                if (next is None) or (not next.startswith('/')) else
                url_for('main.index')
            )
            return redirect(next)
