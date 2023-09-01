import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # (*) Enable and use the 'App Password' in your Google account,
    # your regular account password won't work.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = (
        os.environ.get('MAIL_USE_TLS', 'true').lower()
        in ['true', 'on', '1']
    )
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # (*)
    MAIL_SUBJECT_PREFIX = '[Flasky]'
    MAIL_SENDER = f'Flasky Admin <{os.environ.get("MAIL_USERNAME")}>'
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DEV_DATABASE_URL') or
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('TEST_DATABASE_URL') or
        'sqlite://'
    )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
