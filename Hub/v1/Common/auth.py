"""Authentication helpers."""
from functools import wraps
from flask import request, Response
from Hub.v1.Common.User import User

def _check_credentials(username, userpassword):
    """Check if user & pass valid."""
    user = User.get_user(username)
    if user != None:
        return user.check_password(userpassword)
    else:
        return False

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    """ Wrapper for HTTP basic auth."""
    @wraps(f)
    def decorated(*args, **kwargs):
        """ Wrapper for HTTP basic auth."""
        auth = request.authorization
        if not auth or not _check_credentials(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
