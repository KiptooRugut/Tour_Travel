from distutils.command.config import config
from flask import Flask
from config import Config, config_options
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_mail import Mail
from flask_simplemde import SimpleMDE



db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()
simple = SimpleMDE()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
photos = UploadSet('photos', IMAGES)
mail = Mail()

def create_app(config_name):
    app = Flask(__name__)
    # app.secret_key = settings.SECRET_KEY
    # app.secret_key = settings.SECRET_KEY

    app.config.from_object(config_options[config_name])
    config_options[config_name].init_app(app)

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    mail.init_app(app)
    simple.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/user-account')

    configure_uploads(app, photos)

    return app