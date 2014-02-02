"""Authentication helpers."""
from functools import wraps
from hashlib import sha256
import json

from datetime import datetime, timedelta

from Hub.api import couch

from flask import request, make_response
from Hub import app

def get_session():
    """Get session_id of current session."""
    if request.headers['content-type'] == "application/json":
        params = request.get_json(silent=True, cache=True)
    else:
        params = request.args
    if 'session' in list(params):
        return params['session']
    else:
        return ""

def _check_session(session):
    """
    Check sessions DB for active session matching session ID

    Runs for each API call
    Return True if session exists, is active, within timeout period,
    and was created with same IP as current request
    """
    app.logger.debug("Checking DB for session %s" % (session))
    session_db = couch['sessions']
    if session in session_db:
        if session_db[session]['active'] == False:
            app.logger.error("Session %s inactive" % (session))
            return False
        elif not (datetime.now() -
                  datetime.strptime(session_db[session]['established'],
                                '%Y-%m-%dT%H:%M:%SZ')) < timedelta(minutes=5):
            app.logger.error("Session %s expired, \
                currenttime: %s, \
                sessiontime: %s" %
                (session, datetime.now(), session_db[session]['established']))
            return False
        else:
            app.logger.debug("Session %s found in DB" % (session))
            return True
    else:
        app.logger.error("Session %s not found in DB" % (session))
        return False

def _check_credentials(username, userpassword):
    """Check if user & pass valid."""
    user_db = couch['users']
    for user_id in user_db:
        if user_db[user_id]['username'] == username:
            dbpasswordhash, salt = user_db[user_id]['password'].split(':')
            userpasswordhash = sha256(salt.encode() +
                                      userpassword.encode()).hexdigest()
            dbprivilege = user_db[user_id]['privilege']

    if userpasswordhash == dbpasswordhash:
        return True, dbprivilege

    return False, "", ""

def requires_auth(f):
    """ Wrapper function to parse session ID, pass to _check_session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        """ Wrapper function to parse session ID, pass to _check_session."""
        if request.headers['content-type'] == "application/json":
            params = request.get_json(silent=True, cache=True)
        else:
            params = request.args

        if 'session' in list(params):
            if not _check_session(params['session']):
                return make_response(
                    json.dumps({"reason" : "BadOrInactiveSession"}),
                    401)

        elif 'username' in list(params) and 'password' in list(params):
            if not _check_credentials(params['username'],
                                      params['password'])[0]:
                return make_response(json.dumps({"reason" : "BadUserOrPass"}),
                                     401)

        else:
            return make_response(json.dumps({"reason" : "NoAuthProvided"}),
                                 401)

        return f(*args, **kwargs)
    return decorated
