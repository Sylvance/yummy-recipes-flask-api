""" The tests for the app"""
import unittest
import json
import time
import os
from flask import current_app
from flask_testing import TestCase
from app import APP, DB
from app.models import User

class BasicTestCase(unittest.TestCase):
    """ The Basic Test case for this APP"""

    def test_index(self):
        """ A test"""
        tester = APP.test_client(self)
        response = tester.get('/', content_type='text/plain')
        self.assertEqual(response.status_code, 200)

class BaseTestCase(TestCase):
	""" Foundation tests"""
    def create_app(self):
        """ Create an instance of the app with the testing configuration :return: """
        APP.config.from_object('app.config.TestingConfig')
        return APP

    def setupdb(self):
        """ Create the database :return: """
        DB.create_all()
        DB.session.commit()

    def removedb(self):
        """ Drop the database tables and also remove the session :return: """
        DB.session.remove()
        DB.drop_all()

    def register_user(self, email, password):
        """ Helper method for registering a user with dummy data :return: """
        return self.client.post(
            '/auth/register',
            content_type='application/json',
            data=json.dumps(dict(email=email, password=password)))

    def get_user_token(self):
        """ Get a user token :return: """
        auth_res = self.register_user('sylvance@gmail.com', 'password')
        return json.loads(auth_res.data.decode())['authentication_token']

    def create_category(self, token):
        """ Helper function to create a category :return: """
        response = self.client.post(
            '/category/',
            data=json.dumps(dict(name='Indian')),
            headers=dict(Authorization='Bearer ' + token),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['status'], 'success')
        self.assertTrue(data['name'], 'Travel')
        self.assertIsInstance(data['id'], int, msg='Value should be a string')

    def create_recipes(self, token):
        """ Helper function to create a recipe :return: """
        recipes = [
            {'name': 'Chapati'},
            {'name': 'Roti'},
            {'name': 'Parantha'},
            {'name': 'Ugali'},
            {'name': 'Mukimo'},
            {'name': 'Kachumbari'},
        ]
        for recipe in recipes:
            response = self.client.post(
                '/recipes/',
                data=json.dumps(dict(name=recipe['name'])),
                headers=dict(Authorization='Bearer ' + token),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertTrue(data['status'], 'success')
            self.assertTrue(data['name'], recipe['name'])
            self.assertIsInstance(data['id'], int, msg='Value should be a string')

class TestAuthentication(BaseTestCase):
    """ Tests for the authentication urls"""
    def test_registration(self):
        """ Test a user is successfully created through the api :return: """
        with self.client:
            response = self.register_user('sylvance@gmail.com', 'password')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered')
            self.assertTrue(data['authentication_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_rgr_type_not_json(self):
        """ Test the content type is application/json :return: """
        with self.client:
            response = self.register_user_with_wrong_request_content_type('sylvance@gmail.com', 'password')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed', msg='Should return failed')
            self.assertTrue(data['message'] == 'Content-type must be json')
            self.assertEqual(response.status_code, 400)

    def test_rgr_missing_email_pswd(self):
        """ Test that the email and password are set when sending the request :return: """
        with self.client:
            response = self.register_user("", "")
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed', msg='Should return failed')
            self.assertTrue(data['message'] == 'Missing or wrong email format or password is less than six characters')

    def test_email_validity(self):
        """ Check that the user has supplied a valid email address. :return: """
        with self.client:
            response = self.register_user('sylvance', 'starwars')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed', msg='Should return failed')
            self.assertTrue(data['message'] == 'Missing or wrong email format or password is less than six characters')

    def test_pswd_length_is_gtr_than_six(self):
        with self.client:
            response = self.register_user('sylvance@gmail.com', '123')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed', msg='Should return failed')
            self.assertTrue(data['message'] == 'Missing or wrong email format or password is less than six characters')

    def test_is_already_registered(self):
        """ Test that the user already exists. :return: """
        user = User('sylvance@gmail.com', 'password')
        DB.session.add(user)
        DB.session.commit()

        with self.client:
            response = self.register_user('sylvance@gmail.com', 'password')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Failed, User already exists, Please sign In')
            self.assertEqual(response.status_code, 400)

    def test_can_login(self):
        """ Register and login in a user :return: """
        with self.client:
            self.register_and_login_in_user()

    def test_lgn_req_payload_is_json(self):
        """ Test that the content type is application/json :return: """
        with self.client:
            response = self.client.post(
                '/authentication/login',
                content_type='application/javascript',
                data=json.dumps(dict(email='example@gmail.com', password='starwars')))
            data = json.loads(response.data.decode())
            self.assertTrue(response.content_type == 'application/json',
                            msg='The content type must be application/json')
            self.assertTrue(response.status_code, 202)
            self.assertTrue(data['status'] == 'failed', msg='failed must be returned')
            self.assertTrue(data['message'] == 'Content-type must be json', msg='Check the returned message')

    def test_lgn_has_incorrect_email_pswd(self):
        """ Test the email of the user trying to login is valid and the password length is greater than 6 characters :return: """
        with self.client:
            response = self.login_user('sylvancegmail.com', 'starwars')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(response.content_type == 'application/json')
            self.assertTrue(data['status'] == 'failed', msg='Status should be failed')
            self.assertTrue(data['message'] == 'Missing or wrong email format or password is less than six characters')

    def test_lgn_does_not_exist_or_pswds_incorrect(self):
        """ Test that the user does not exist or the password is incorrect :return: """
        with self.client:
            response = self.login_user('sylvance@gmail.com', 'starwars')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'User does not exist or password is incorrect')

    def test_valid_user_log_out(self):
        """ Test that s user is logged out with a valid auth token :return: """
        with self.client:
            # Register and login user
            login_data = self.register_and_login_in_user()
            # Logout user
            logout_response = self.logout_user(login_data['authentication_token'])
            logout_data = json.loads(logout_response.data.decode())
            self.assertEqual(logout_response.status_code, 200)
            self.assertTrue(logout_data['status'] == 'success')
            self.assertTrue(logout_data['message'] == 'Successfully logged out')

    def test_expired_user_token_user_log_out(self):
        """ Try to log out a user whose auth token has expired. :return: """
        with self.client:
            login_data = self.register_and_login_in_user()
            # Pause for 3 seconds
            time.sleep(self.app.config['TOKEN_EXPIRATION_TESTS'])
            # Logout user
            logout_response = self.logout_user(login_data['authentication_token'])
            logout_data = json.loads(logout_response.data.decode())
            self.assertTrue(logout_data['status'] == 'failed')
            self.assertTrue(logout_data['message'] == 'Signature expired, Please sign in again')
            self.assertEqual(logout_response.status_code, 401)

    def test_log_out_contains_an_authorization_header(self):
        """ Test that the authorization header is set :return: """
        with self.client:
            response = self.client.post(
                'authentication/logout',
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Provide an authorization header')
            self.assertEqual(response.status_code, 403)

    def test_log_out_has_a_valid_token(self):
        """ Test that a valid authorization token has been sent within the header :return: """
        with self.client:
            response = self.client.post(
                'auth/logout',
                headers=dict(Authorization='Bearersdfsdvfj.bvdfvbdfxcvxcxcv')
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Provide a valid auth token')
            self.assertEqual(response.status_code, 403)

    def test_token_was_banned(self):
        """ Test that the auth token has already been added to the Blaclisted tokens table, so a user cannot log out. :return: """
        with self.client:
            # Register and login user
            login_data = self.register_and_login_in_user()
            # Logout user
            logout_response = self.logout_user(login_data['authentication_token'])
            logout_data = json.loads(logout_response.data.decode())
            self.assertEqual(logout_response.status_code, 200)
            self.assertTrue(logout_data['status'] == 'success')
            self.assertTrue(logout_data['message'] == 'Successfully logged out')

            logout_again_response = self.logout_user(login_data['authentication_token'])
            logout_again_data = json.loads(logout_again_response.data.decode())
            self.assertEqual(logout_again_response.status_code, 401)
            self.assertTrue(logout_again_data['status'] == 'failed')
            self.assertTrue(logout_again_data['message'] == 'Token was banned, Please login In')

    def test_token_required_method_incorrect(self):
        """ Test that the sent authorization header is incorrect :return: """
        with self.client:
            response = self.client.get(
                '/category/',
                headers=dict(Authorization='Bearerfgghjkljkhjvhbjn')
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 403)
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Provide a valid auth token')

    def test_token_required_method_missing(self):
        """ Test that the authorization token is missing on a request to get private user data :return: """
        with self.client:
            response = self.client.get(
                '/category/'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Token is missing')

    def test_token_required_method_invalid(self):
        """ Test that the authorization token is invalid on a request to get private user data :return: """
        with self.client:
            response = self.client.get(
                '/category/',
                headers=dict(Authorization='Bearer fgghjkljkhjvhbjn.sdfsdgfgfg')
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Invalid token. Please sign in again')

    def test_token_required_method_banned(self):
        """ Test that the token being used to access a user resource was banned :return: """
        with self.client:
            # Register and login a user
            json_response = self.register_and_login_in_user()
            # Logout a user
            token = json_response['authentication_token']
            self.logout_user(token)
            # Send a Get request to category endpoint
            response = self.client.get(
                '/category/',
                headers=dict(Authorization='Bearer ' + token)
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Token was banned, Please login In')

    def test_token_required_method_expired(self):
        """ Test that the token being used to access a user resource has expired :return: """
        with self.client:
            # Register and login a user
            json_response = self.register_and_login_in_user()
            token = json_response['authentication_token']
            # Pause method for 3 seconds for the token to expire
            time.sleep(self.app.config['TOKEN_EXPIRATION_TESTS'])
            # Send a Get request to category endpoint
            response = self.client.get(
                '/category/',
                headers=dict(Authorization='Bearer ' + token)
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(data['status'] == 'failed')
            self.assertTrue(data['message'] == 'Signature expired, Please sign in again')

    def register_and_login_in_user(self):
        """ Helper method to sign up and login a user :return: Json login response """
        reg_response = self.register_user('sylvance@gmail.com', 'starwars')
        data = json.loads(reg_response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'Successfully registered')
        self.assertTrue(data['authentication_token'])
        self.assertTrue(reg_response.content_type == 'application/json')
        self.assertEqual(reg_response.status_code, 201)
        # Login the user
        login_response = self.client.post(
            'auth/login',
            data=json.dumps(dict(email='sylvance@gmail.com', password='starwars')),
            content_type='application/json'
        )
        login_data = json.loads(login_response.data.decode())
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_data['authentication_token'])
        self.assertTrue(login_data['status'] == 'success')
        self.assertTrue(login_data['message'] == 'Successfully logged In')
        self.assertTrue(login_response.content_type == 'application/json')
        return login_data

    def logout_user(self, token):
        """ Helper method to log out a user :param token: Auth token :return: """
        logout_response = self.client.post(
            'auth/logout',
            headers=dict(Authorization='Bearer ' + token)
        )
        return logout_response

    def register_user_with_wrong_request_content_type(self, email, password):
        """ Helper method to register a user using a wrong content-type :param email: Email :param password: Password :return: """
        return self.client.post(
            '/authentication/register',
            content_type='application/javascript',
            data=json.dumps(dict(email=email, password=password)))

    def login_user(self, email, password):
        """ Helper method to login a user :param email: Email :param password: Password :return: """
        return self.client.post(
            '/authentication/login',
            content_type='application/json',
            data=json.dumps(dict(email=email, password=password)))

    def test_can_reset_password(self):
        """ Test that a password is successfully reset. :return: """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['authentication_token']
            response = self.client.post(
                '/authentication/reset/password',
                headers=dict(Authorization='Bearer ' + token),
                content_type='application/json',
                data=json.dumps(dict(oldPassword='starwars', newPassword='warsdome',
                                     passwordConfirmation='warsdome')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(res['status'] == 'success')
            self.assertTrue(res['message'] == 'Password reset successfully')

    def test_failed_content_type_not_json(self):
        """ Test a request fails if content type is not json :return: """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['authentication_token']
            response = self.client.post(
                '/authentication/reset/password',
                headers=dict(Authorization='Bearer ' + token),
                data=json.dumps(dict(oldPassword='starwars', newPassword='warsdome',
                                     passwordConfirmation='warsdome')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertTrue(res['status'] == 'failed')
            self.assertTrue(res['message'] == 'Content type must be json')

    def test_incorrect_old_password(self):
        """ Test that the user supplied an incorrect password :return: """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['authentication_token']
            response = self.client.post(
                '/authentication/reset/password',
                content_type='application/json',
                headers=dict(Authorization='Bearer ' + token),
                data=json.dumps(dict(oldPassword='stars', newPassword='warsdome',
                                     passwordConfirmation='warsdome')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(res['status'] == 'failed')
            self.assertTrue(res['message'] == 'Incorrect password')

    def test_unincluded_attributes(self):
        """ Test that some attributes are not included in the request. :return: """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['authentication_token']
            response = self.client.post(
                '/authentication/reset/password',
                content_type='application/json',
                headers=dict(Authorization='Bearer ' + token),
                data=json.dumps(dict(oldPassword='starwars', newPassword='warsdome')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertTrue(res['status'] == 'failed')
            self.assertTrue(res['message'] == 'Missing required attributes')

    def test_not_match_confirmation(self):
        """ Test that the new password does not match the password confirmation. :return: """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['authentication_token']
            response = self.client.post(
                '/authentication/reset/password',
                headers=dict(Authorization='Bearer ' + token),
                content_type='application/json',
                data=json.dumps(dict(oldPassword='starwars', newPassword='warsdome',
                                     passwordConfirmation='vitadome')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertTrue(res['status'] == 'failed')
            self.assertTrue(res['message'] == 'New password does not match')

    def test_failed_pswd_lt_six(self):
        """ Test that a failed status message is returned when new password is six characters and below. :return: """
        with self.client:
            login_data = self.register_and_login_in_user()
            token = login_data['authentication_token']
            response = self.client.post(
                '/authentication/reset/password',
                headers=dict(Authorization='Bearer ' + token),
                content_type='application/json',
                data=json.dumps(dict(oldPassword='starwars', newPassword='wars',
                                     passwordConfirmation='wars')))
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertTrue(res['status'] == 'failed')
            self.assertTrue(res['message'] == 'New password should be greater than six characters long')

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
