""" Views file for the Flask APP"""

from app import APP

@APP.route('/')
@APP.route('/index')
def index():
    """ Return statement """
    return "Hello Yummy recipes"

# set the secret key.  keep this really secret:
APP.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    APP.run(debug=True,
            host="0.0.0.0",
            port="8888")
