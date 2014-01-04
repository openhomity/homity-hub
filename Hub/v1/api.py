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
    sessionDB = couch['sessions']
    oldIds = []
    for id in sessionDB:
        if sessionDB[id]['active'] == False or (datetime.now() - datetime.strptime(sessionDB[id]['established'], '%Y-%m-%dT%H:%M:%SZ')) > timedelta(minutes = 5):
            oldIds.append(id)
    for id in oldIds:
        app.logger.debug("Deleting session %s" % id)
        del sessionDB[id]
    app.logger.debug('Session cleanup complete')
    
def _async_logins(session, sessionDB, alarmSLT):
    _camera_login(session, sessionDB)
    _alarm_login(session, sessionDB, alarmSLT)

"""
Login method/API, uses POST verb and expects JSON body with credentials
Usage - POST /login -d {"username":username, "password":password}

If credentials are good, all stateful logins are processed in another thread (Alarm, BlueIris), and session is created in sessionDB with -
- Username & privilege level copied from users DB
- IP of user
- Creation time

""" 
@v1api.route('/v1/login', methods = ['POST'])
def loginPOST():
    global cameraInfo
    
    cleanup_thread = Thread(target = _session_cleanup, args = [])
    cleanup_thread.start()

    if request.headers['content-type'] == "application/json":
        args = request.get_json(silent=True, cache=True)
    else:
        args = request.args
    
    if not ('username' in list(args) and 'password' in list(args)):
        app.logger.error("Missing Username or PW for login attempt, got %s" % (args))
        return make_response(json.dumps({"reason" : "MissingUserorPW"}),401)
    
    remoteAddr = request.remote_addr
    username = args['username']
    password = args['password']

    quick = True
        
    app.logger.info("Login request for user %s from %s, quick=%s" % (username, remoteAddr, quick))
    login_result, dbprivilege, alarmSLT = _check_credentials(username, password)
    
    if login_result:
        sessionDB = couch['sessions']
        session = Session(user=username,privilege=dbprivilege,active=True, established=datetime.now(), remoteAddr=remoteAddr)
        session.store(sessionDB)
        returnInfo = {"result" : "success", "session" : session.id}
        app.logger.info("Session created in for user %s session %s IP %s" % (username,session.id, remoteAddr))
        currentSession = session.id
        app.logger.debug("Starting login for camera & alarm, async=%s" % (quick))
        if quick:
            camera_session = ""
            alarm_session = ""
            async_login_thread = Thread(target = _async_logins, args = [session, sessionDB, alarmSLT])
            async_login_thread.start()
        else:
            if _camera_login(session, sessionDB):
                app.logger.debug("Camera logged in for user:%s" % (username))
            else:
                app.logger.debug("Camera login failed for user:%s" % (username))
            
            if _alarm_login(session, sessionDB, alarmSLT):
                app.logger.debug("Alarm logged in for user:%s" % (username))
            else:
                app.logger.debug("Alarm login failed for user:%s" % (username))
        
    else:
        app.logger.error("Bad Username or PW for user:%s" % (username))
        return make_response(json.dumps({"reason" : "BadUserorPW"}),401)
    
    return json.dumps(returnInfo)

"""
Logout method/API, uses POST verb and expects JSON body with session ID
Usage - POST /logout -d {"session":session}

If session exists, logs out of camera & deletes session

Todo - figure out how to log out of alarm

""" 
@v1api.route('/v1/logout', methods = ['POST'])
@requires_auth
def logoutPOST():
    currentSession = get_session()
    
    if currentSession == "":
        return make_response(json.dumps({"reason" : "BadOrInactiveSession"}),401)
    
    app.logger.debug("Logout request for session %s" % (currentSession))
    sessionDB = couch['sessions']
    
    cameraSession = sessionDB[currentSession]['cameraSession']

    cameraDB = couch['camera']
    for id in cameraDB:
        cameraObject = BlueIris.load(cameraDB,id)

    cameraObject.setSession(cameraSession)
    
    if cameraObject.logout():
        app.logger.debug("Camera logout successful for session %s" % (currentSession))
    else:
        app.logger.debug("Camera logout failed for session %s" % (currentSession))
        
    del sessionDB[currentSession]
    
    return ""
