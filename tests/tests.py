""" The tests for the app"""
import unittest

from app import APP


class BasicTestCase(unittest.TestCase):
    """ The Basic Test cases for this APP"""

    def test_index(self):
        """ A test"""
        tester = APP.test_client(self)
        response = tester.get('/', content_type='text/plain')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
