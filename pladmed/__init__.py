import os
from flask_cors import CORS
from flask import Flask
from pladmed.database import Database
from pladmed.models.token import Token
import logging
from flask_socketio import SocketIO
from pladmed.utils.encoders import JsonEncoder
from flask_mail import Mail, Message

socketio = SocketIO(async_mode="eventlet")

def init_database(config):
    return Database(
        config["MONGO_USER"],
        config["MONGO_PASSWORD"],
        config["MONGO_HOST"],
        config["MONGO_PORT"],
        config["MONGO_DB"]
    )

def init_logging(config):
    logging.basicConfig(
        format='%(asctime)s || %(levelname)s: %(message)s',
        filename='logs/' + os.getenv('LOG_FILE', 'default_logs'),
        level=logging.DEBUG
    )

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        MONGO_USER=os.getenv('MONGO_USERNAME', 'user'),
        MONGO_PASSWORD=os.getenv('MONGO_PASSWORD', 'password'),
        MONGO_HOST=os.getenv('MONGO_HOST', 'localhost'),
        MONGO_PORT=os.getenv('MONGO_PORT', "27017"),
        MONGO_DB=os.getenv('MONGO_DATABASE', 'pladmed')
    )
    app.config['MAIL_SERVER']=os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT', 587)
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'nicolas.g.calvo@gmail.com')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'zjmipowaztropdfn')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', True)
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', False)
    app.config['MAIL_DEBUG'] = os.getenv('MAIL_DEBUG', True)
    mail = Mail(app)

    if test_config is None:
        init_logging(app.config)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.db = init_database(app.config)
    app.probes = {}
    app.token = Token(app.config["SECRET_KEY"])
    app.json_encoder = JsonEncoder

    logging.info('Se registrará el blueprint api.')
    from pladmed.routes import api, superuser
    app.register_blueprint(api)
    app.register_blueprint(superuser)

     # blueprint for auth routes in our app
    logging.info('Se registrará el blueprint authorization.')
    from pladmed.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    CORS(app)

    socketio.init_app(app)

    return app
