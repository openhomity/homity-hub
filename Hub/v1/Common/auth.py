from functools import wraps
from hashlib import sha256
import json

from datetime import datetime, timedelta

from couchdb import Server
from Hub.api import couch

from flask import request,make_response
from Hub import app

def get_session():
    if request.headers['content-type'] == "application/json":
        params = request.get_json(silent=True, cache=True)
    else:
        params = request.args
    if 'session' in list(params):
        return params['session']
    else:
        return ""

"""
Check sessions DB for active session matching session ID
Runs for each API call
Return True if session exists, is active, within timeout period, and was created with same IP as current request
""" 
def _check_session(session):
    app.logger.debug("Checking DB for session %s" % (session))
    global currentSession
    sessionDB = couch['sessions']
    if session in sessionDB:
        if sessionDB[session]['active'] == False:
            app.logger.error("Session %s inactive" % (session))
            return False
        elif not (datetime.now() - datetime.strptime(sessionDB[session]['established'], '%Y-%m-%dT%H:%M:%SZ')) < timedelta(minutes = 5):
            app.logger.error("Session %s expired, currenttime: %s, sessiontime: %s" % (session, datetime.now(), sessionDB[session]['established']))
            return False
            """
            #removed check below due to GAppEngine often coming in from different IPs
        elif sessionDB[session]['remoteAddr'] != request.remote_addr:
            app.logger.error("Session %s was established from a different IP, original: %s, latest: %s" % (session, sessionDB[session]['remoteAddr'], request.remote_addr))
            return False
            """
        else:
            currentSession = session
            app.logger.debug("Session %s found in DB" % (session))
            return True
    else:
        app.logger.error("Session %s not found in DB" % (session))
        return False
    
def _check_credentials(username, userpassword):
    userDB = couch['users']
    for id in userDB:
        if userDB[id]['username'] == username:
            dbpasswordhash, salt = userDB[id]['password'].split(':')
            userpasswordhash = sha256(salt.encode() + userpassword.encode()).hexdigest()
            dbprivilege = userDB[id]['privilege']
            alarmSLT = userDB[id]['alarmSLT']
    
    if not id:
        app.logger.error("Bad user:%s" % (username))
        return False, "", ""
    
    if userpasswordhash == dbpasswordhash:
        return True, dbprivilege, alarmSLT
    
    return False, "", ""

"""
Wrapper function to parse session ID, pass to _check_session
Todo
- Check Content-Type before parsing session id
""" 
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers['content-type'] == "application/json":
            params = request.get_json(silent=True, cache=True)
        else:
            params = request.args
            
        if 'session' in list(params):
            if not _check_session(params['session']):
                return make_response(json.dumps({"reason" : "BadOrInactiveSession"}),401)
        elif 'username' in list(params) and 'password' in list(params):
            if not _check_credentials(params['username'], params['password']):
                return make_response(json.dumps({"reason" : "BadUserOrPass"}),401)
        else:
            return make_response(json.dumps({"reason" : "NoAuthProvided"}),401)
        
        return f(*args, **kwargs)
    return decorated