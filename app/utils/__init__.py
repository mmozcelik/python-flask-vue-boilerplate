from functools import wraps

from flask import current_app, request, Response, Blueprint

import hashlib


def capitalize_all(s):
    if isinstance(s, str):
        return " ".join(w.capitalize() for w in s.split())

    return s


def add_basic_auth(blueprint: Blueprint, username, password, realm='api'):
    """
    Add HTTP Basic Auth to a blueprint.
    Note this is only for casual use!
    """

    @blueprint.before_request
    def basic_http_auth(*args, **kwargs):
        auth = request.authorization
        if auth is None or auth.password != password or auth.username != username:
            return Response('Please login', 401, {'WWW-Authenticate': f'Basic realm="{realm}"'})


def check_auth(username, password):
    """
    This function is called to check if a username /
    password combination is valid.
    """
    return username == current_app.config['DOC_USERNAME'] and password == current_app.config['DOC_PASSWORD']


def authenticate():
    """
    Sends a 401 response that enables basic auth
    """
    return Response('Not Authorized', 401, {'WWW-Authenticate': 'Basic realm="api"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def clean_str(value):
    if not isinstance(value, str):
        return value

    try:
        value = value.encode('utf-8')
    except:
        pass

    return value


class BCrypt(object):
    @classmethod
    def hash(cls, password, salt=None):
        return hashlib.sha256(clean_str(password)).hexdigest()
