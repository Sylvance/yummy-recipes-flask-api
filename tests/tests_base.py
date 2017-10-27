""" Tests foundation"""
from app import APP, DB
from flask_testing import TestCase
import json


class BaseTestCase(TestCase):
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
