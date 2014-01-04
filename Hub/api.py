from flask import current_app,request,make_response,abort

import logging
from functools import wraps

from Hub import app

from ConfigParser import SafeConfigParser, NoOptionError
from couchdb import Server
from v1.Common.helpers import bool_or_string

'''
Parse Config
'''
hub_config = {}
hub_config_parser = SafeConfigParser()
hub_config_parser.read('/etc/homity/homityhub.conf')

try:
    hub_config['logger_path'] = hub_config_parser.get('logger','path')
except NoOptionError:
    hub_config['logger_path'] = ""
    hub_config['logger_enabled'] = False
    
try: 
    hub_config['couch_url'] = hub_config_parser.get('couchdb','server')
    hub_config['couch_username'] = hub_config_parser.get('couchdb','username')
    hub_config['couch_password'] = hub_config_parser.get('couchdb','password')
except NoOptionError:
    hub_config['couch_url'] = ""
    hub_config['couch_username'] = ""
    hub_config['couch_password'] = ""

try:
    hub_config['ssl_enable'] = bool_or_string(hub_config_parser.get('ssl','enabled'))
except NoOptionError:
    hub_config['ssl_enable'] = False

if hub_config['ssl_enable']:
    try:
        hub_config['ssl_private_key'] = hub_config_parser.get('ssl','private_key_path')
        hub_config['ssl_cert'] = hub_config_parser.get('ssl','cert_path')
    except NoOptionError:
        hub_config['ssl_enable'] = False

'''
Set up Logger 
'''
file_handler = logging.FileHandler(hub_config.get('logger_path'))
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
))
app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)
log.addHandler(file_handler)


'''
Set up CouchDB
'''
couch = Server(url=hub_config.get('couch_url'))
couch.resource.credentials = (hub_config.get('couch_username'), hub_config.get('couch_password'))


@app.route('/', methods = ['GET'])
def get_all_status():
    return ""
