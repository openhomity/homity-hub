from couchdb import Server
from flask import Blueprint, current_app,request,make_response,abort
import json
import logging
from functools import wraps
from datetime import datetime, timedelta
from threading import Thread

from Hub import app
from Hub.api import couch
from Hub.v1.Common.auth import requires_auth, _check_credentials, get_session

from Hub.v1.Common.Session import Session
from Hub.v1.Common.User import User


v1api = Blueprint('v1api', __name__)

"""
Walk sessions DB and purge inactive or timed out sessions
Called once per /login
"""
def _session_cleanup():
    app.logger.debug('Starting session cleanup')
    session_db = couch['sessions']
    expired_sessions = []
    for id in session_db:
        if session_db[id]['active'] == False or (datetime.now() - datetime.strptime(session_db[id]['established'], '%Y-%m-%dT%H:%M:%SZ')) > timedelta(minutes = 5):
            expired_sessions.append(id)
    for id in expired_sessions:
        app.logger.debug("Deleting session %s" % id)
        del session_db[id]
    app.logger.debug('Session cleanup complete')

"""
Login method/API, uses POST verb and expects JSON body with credentials
Usage - POST /login -d {"username":username, "password":password}

If credentials are good, all stateful logins are processed in another thread (Alarm, Camera), and session is created in session_db with -
- Username & privilege level copied from users DB
- IP of user
- Creation time

""" 
@v1api.route('/v1/login', methods = ['POST'])
def loginPOST():  
    cleanup_thread = Thread(target = _session_cleanup, args = [])
    cleanup_thread.start()

    if request.headers['content-type'] == "application/json":
        args = request.get_json(silent=True, cache=True)
    else:
        args = request.args
    
    if not ('username' in list(args) and 'password' in list(args)):
        app.logger.error("Missing Username or PW for login attempt, got %s" % (args))
        return make_response(json.dumps({"reason" : "MissingUserorPW"}),401)
    
    remote_address = request.remote_addr
    username = args['username']
    password = args['password']
        
    app.logger.info("Login request for user %s from %s, quick=%s" % (username, remote_address, quick))
    login_result, dbprivilege = _check_credentials(username, password)
    
    if login_result:
        session_db = couch['sessions']
        session = Session(user=username,privilege=dbprivilege,active=True, established=datetime.now(), remoteAddress=remote_address)
        session.store(session_db)
        return_info = {"result" : "success", "session" : session.id}
        app.logger.info("Session created in for user %s session %s IP %s" % (username,session.id, remote_address))
        current_session = session.id
        
        def async_logins():
            pass #add functions that need stateful login here
        async_login_thread = Thread(target = async_logins, args = [session, session_db])
        async_login_thread.start()
        
    else:
        app.logger.error("Bad Username or PW for user:%s" % (username))
        return make_response(json.dumps({"reason" : "BadUserorPW"}),401)
    
    return json.dumps(return_info)

"""
Logout method/API, uses POST verb and expects JSON body with session ID
Usage - POST /logout -d {"session":session}

If session exists, logs out of camera & deletes session

Todo - figure out how to log out of alarm

""" 
@v1api.route('/v1/logout', methods = ['POST'])
@requires_auth
def logoutPOST():
    current_session = get_session()
    
    if current_session == "":
        return make_response(json.dumps({"reason" : "BadOrInactiveSession"}),401)
    
    app.logger.debug("Logout request for session %s" % (current_session))
    session_db = couch['sessions']
        
    del session_db[current_session]
    
    return ""
