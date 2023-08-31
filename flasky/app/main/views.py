from threading import Thread

from flask import current_app, session, redirect, render_template, url_for
from flask_mail import Message
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from . import main
from .. import db, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(
        current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
        sender=current_app.config['MAIL_SENDER'],
        recipients=[to]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[current_app, msg])
    thr.start()
    return thr


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(64),
        unique=True,
        index=True
    )
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return f'<User {self.username}>'


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@main.route('/', methods=['GET', 'POST'])
def index():
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
            if current_app.config['MAIL_RECIPIENT']:
                send_email(
                    to=current_app.config['MAIL_RECIPIENT'],
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


@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
