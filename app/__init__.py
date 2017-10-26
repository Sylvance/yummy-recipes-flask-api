""" This main application initialisation """
from flask import Flask

APP = Flask(__name__)
# APP.config.from_object('config')

from app import views
