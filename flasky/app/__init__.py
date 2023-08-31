import os

from dotenv import load_dotenv
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy


load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()


def create_app():
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

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app