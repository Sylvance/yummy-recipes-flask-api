""" Views file for the Flask APP"""
from app import APP
from app.helpers.response_helper import response

@APP.route('/')
@APP.route('/index')
def index():
    """ Return statement """
    return "Hello Yummy recipes"


@APP.errorhandler(404)
def route_not_found(e):
    """ Return a custom 404 Http response message for missing or not found routes. :param e: Exception :return: Http Response """
    return response('failed', 'Endpoint not found', 404)


@APP.errorhandler(405)
def method_not_found(e):
    """ Custom response for methods not allowed for the requested URLs :param e: Exception :return: """
    return response('failed', 'The method is not allowed for the requested URL', 405)


@APP.errorhandler(500)
def internal_server_error(e):
    """ Return a custom message for a 500 internal error :param e: Exception :return: """
    return response('failed', 'Internal server error', 500)


# set the secret key.  keep this really secret:
APP.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    APP.run(debug=True,
            host="0.0.0.0",
            port="8888")
