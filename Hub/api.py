"""
Load Homity Config, Start Services
"""
import logging

from Hub import app
from Hub.v1.Common.auth import requires_auth
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from couchdb import Server
from v1.Common.helpers import bool_or_string

'''
Parse Config
'''
hub_config = {}
hub_config_parser = SafeConfigParser()
hub_config_parser.read('/etc/homity/homityhub.conf')

try:
    hub_config['logger_path'] = hub_config_parser.get('logger',
                                                      'path')
except (NoOptionError, NoSectionError):
    hub_config['logger_path'] = False

try:
    hub_config['couch_url'] = hub_config_parser.get('couchdb',
                                                    'server')
except (NoOptionError, NoSectionError):
    hub_config['couch_url'] = False
try:
    hub_config['couch_username'] = hub_config_parser.get('couchdb',
                                                         'username')
    hub_config['couch_password'] = hub_config_parser.get('couchdb',
                                                         'password')
except (NoOptionError, NoSectionError):
    hub_config['couch_username'] = False
    hub_config['couch_password'] = False

try:
    hub_config['ssl_enable'] = bool_or_string(hub_config_parser.get('ssl',
                                                                    'enabled'))
except (NoOptionError, NoSectionError):
    hub_config['ssl_enable'] = False

if hub_config['ssl_enable']:
    try:
        hub_config['ssl_private_key'] = hub_config_parser.get(
            'ssl',
            'private_key_path')
        hub_config['ssl_cert'] = hub_config_parser.get('ssl',
                                                       'cert_path')
    except (NoOptionError, NoSectionError):
        hub_config['ssl_enable'] = False

'''
Set up Logger 
'''
if hub_config['logger_path']:
    FILE_HANDLER = logging.FileHandler(hub_config.get('logger_path'))
    FILE_HANDLER.setLevel(logging.INFO)
    FILE_HANDLER.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
    ))
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(FILE_HANDLER)

    LOG = logging.getLogger('werkzeug')
    LOG = logging.getLogger('wsgi')
    LOG.setLevel(logging.INFO)
    LOG.addHandler(FILE_HANDLER)


'''
Set up CouchDB
'''
if hub_config['couch_url']:
    couch = Server(url=hub_config.get('couch_url'))
    if hub_config.get('couch_username'):
        couch.resource.credentials = (hub_config.get('couch_username'),
                                      hub_config.get('couch_password'))
else:
    couch = Server(url="http://localhost:5984")

@app.route('/', methods=['GET'])
@requires_auth
def get_all_status():
    """Placeholder for root get."""
    return app.send_static_file('index.html')
    return ""
