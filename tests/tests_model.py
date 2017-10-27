from app import DB
from tests.tests_base import BaseTestCase
from app.models import User
import unittest


class TestUserModel(BaseTestCase):
    """ Test that the auth token is generated correctly """

    def test_encode_user_token(self):
        """ Test that a user token is generated correctly :return: """
        user = self.create_and_save_user()
        auth_token = self.get_token(user)
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_user_token(self):
        """ Test that the user auth token is decoded and that its valid :return: """
        user = self.create_and_save_user()
        auth_token = self.get_token(user)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(user.decode_token(auth_token.decode('utf-8')) == 1, msg='The user Id should be 1')

    def create_and_save_user(self):
        """ Helper method to create and save a user in the database :return: """
        user = User(email='sylvance@gmail.com', password='starwars')
        DB.session.add(user)
        DB.session.commit()
        return user

    def get_token(self, user):
        """ Helper method to decode a user auth token :param user: :return: """
        auth_token = user.encode_token(user.id)
        return auth_token


if __name__ == '__main__':
    unittest.main()
