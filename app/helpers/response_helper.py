""" Response helper"""
from flask import jsonify, make_response

def response(status, message, status_code):
    """ Make an http response helper :param status: Status message :param message: Response Message :param status_code: Http response code :return: """
    return make_response(jsonify({
        'status': status,
        'message': message
    })), status_code

def response_auth(status, message, token, status_code):
    """ Make a Http response to send the auth token :param status: Status :param message: Message :param token: Authorization Token :param status_code: Http status code :return: Http Json response """
    return make_response(jsonify({
        'status': status,
        'message': message,
        'authentication_token': token.decode("utf-8")
    })), status_code
