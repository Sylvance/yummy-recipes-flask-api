""" Configuration file"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
POSTGRES_LOCAL_BASE = 'postgresql://postgres:starwars@localhost/'
DATABASE_NAME = 'yummyrecipesdb'


class BaseConfig:
    """ Base application configuration """
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'this_is_a_super_secret')
    BCRYPT_HASH_PREFIX = 14
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_EXPIRY_DAYS = 7
    TOKEN_EXPIRY_SECONDS = 4000
    PAGINATION = 15


class DevelopmentConfig(BaseConfig):
    """ Development application configuration """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', POSTGRES_LOCAL_BASE + DATABASE_NAME)
    BCRYPT_HASH_PREFIX = 4
    TOKEN_EXPIRY_DAYS = 1
    TOKEN_EXPIRY_SECONDS = 20
    PAGINATION = 4


class TestingConfig(BaseConfig):
    """ Testing application configuration """
    DEBUG = True
    TESTING = True
    POSTFIX = POSTGRES_LOCAL_BASE + DATABASE_NAME + "_test"
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL_TEST', POSTFIX)
    BCRYPT_HASH_PREFIX = 4
    TOKEN_EXPIRY_DAYS = 0
    TOKEN_EXPIRY_SECONDS = 3
    TOKEN_EXPIRATION_TESTS = 5
    PAGINATION = 3


class ProductionConfig(BaseConfig):
    """ Production application configuration """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', POSTGRES_LOCAL_BASE + DATABASE_NAME)
    BCRYPT_HASH_PREFIX = 13
    TOKEN_EXPIRY_DAYS = 30
    TOKEN_EXPIRY_SECONDS = 20
    PAGINATION = 10
