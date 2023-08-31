import os
from datetime import datetime
from threading import Thread

from flask import Flask, session, flash, redirect, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from dotenv import load_dotenv
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' +
    os.path.join(basedir, 'data.sqlite')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['MAIL_SENDER'] = f"Flasky Admin<{os.environ.get('MAIL_USERNAME')}>"
app.config['MAIL_RECIPIENT'] = os.environ.get('MAIL_RECIPIENT')
# Enable and use the 'App Password' in your Google account, 
# your regular account password won't work.
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') 
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)
mail = Mail(app)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(
        app.config['MAIL_SUBJECT_PREFIX'] + subject,
        sender=app.config['MAIL_SENDER'],
        recipients=[to]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
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


@app.route('/', methods=['GET', 'POST'])
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
            if app.config['MAIL_RECIPIENT']:
                send_email(
                    to=app.config['MAIL_RECIPIENT'],
                    subject='New User', 
                    template='mail/new_user', 
                    user=user
                )
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role}


if __name__ == '__main__':
    app.run()
