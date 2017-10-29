from flask_testing import TestCase
from app import APP
from flask import current_app
import unittest
import os


class TestDevelopmentConfig(TestCase):
    """ Test the Development configuration """

    def create_app(self):
        """ Create an APP with the development configuration :return: """
        APP.config.from_object('app.config.DevelopmentConfig')
        return APP

    def test_app_in_development(self):
        """ Test that the development configs are set correctly. :return: """
        self.assertFalse(APP.config['SECRET_KEY'] is 'star wars')
        self.assertTrue(APP.config['DEBUG'], True)
        self.assertTrue(APP.config['BCRYPT_HASH_PREFIX'] == 4)
        self.assertFalse(current_app is None)
        self.assertTrue(APP.config['SQLALCHEMY_DATABASE_URI'] == os.getenv('DATABASE_URL',
                                                                           "postgresql://postgres:starwars@localhost/yummyrecipesdb"))
        self.assertEqual(APP.config['TOKEN_EXPIRY_DAYS'], 1)
        self.assertEqual(APP.config['TOKEN_EXPIRY_SECONDS'], 20)
        self.assertEqual(APP.config['PAGINATION'], 4)


class TestTestingConfig(TestCase):
    """ Test the Testing configuration """

    def create_app(self):
        """ Create an instance of the APP with the testing configuration :return: """
        APP.config.from_object('app.config.TestingConfig')
        return APP

    def test_app_in_testing(self):
        """ Test that the testing configs are set correctly :return: """
        self.assertFalse(APP.config['SECRET_KEY'] is 'star wars')
        self.assertTrue(APP.config['DEBUG'], True)
        self.assertTrue(APP.config['TESTING'] is True)
        self.assertTrue(APP.config['BCRYPT_HASH_PREFIX'] == 4)
        self.assertFalse(current_app is None)
        self.assertTrue(APP.config['SQLALCHEMY_DATABASE_URI'] == os.getenv('DATABASE_URL_TEST',
                                                                           "postgresql://postgres:starwars@localhost/yummyrecipestestdb"))
        self.assertEqual(APP.config['TOKEN_EXPIRY_DAYS'], 0)
        self.assertEqual(APP.config['TOKEN_EXPIRY_SECONDS'], 3)
        self.assertEqual(APP.config['TOKEN_EXPIRATION_TESTS'], 5)
        self.assertEqual(APP.config['PAGINATION'], 3)

if __name__ == '__main__':
    unittest.main()
