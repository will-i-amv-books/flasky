from flask import current_app, session, redirect, render_template, url_for

from . import main
from .. import db
from .forms import NameForm
from ..email import send_email
from ..models import User


@main.route('/', methods=['GET', 'POST'])
def index():
    app = current_app._get_current_object()
    form = NameForm()
    if not form.validate_on_submit():
        return render_template(
            'index.html',
            form=form, 
            name=session.get('name'),
            known=session.get('known', False)
        )
    else:
        user = User.query.filter_by(username=form.name.data).first()
        if user is not None:
            session['known'] = True
        else:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['MAIL_RECIPIENT']:
                send_email(
                    to=app.config['MAIL_RECIPIENT'],
                    subject='New User', 
                    template='mail/new_user', 
                    user=user
                )
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))


@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)
