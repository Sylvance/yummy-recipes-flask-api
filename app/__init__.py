""" This main application initialisation """
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

APP = Flask(__name__)
# APP.config.from_object('config')
# Enabling cors
CORS(APP)

# APP configuration
APP_SETTINGS = os.getenv(
    'APP_SETTINGS',
    'app.config.DevelopmentConfig'
)
APP.config.from_object(APP_SETTINGS)

# Initialize BCRYPT
BCRYPT = Bcrypt(APP)

# Initialize Flask Sql Alchemy
DB = SQLAlchemy(APP)


from app import views

# Register blue prints
from app.controllers.auth import authentication

APP.register_blueprint(authentication)
