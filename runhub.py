"""
Launcher for homity-hub
"""
from Hub import app
from Hub.api import hub_config

import cherrypy
from paste.translogger import TransLogger

if hub_config.get('ssl_enable'):
    from OpenSSL import SSL

def run_server():
    """Enable WSGI access logging via Paste"""
    app_logged = TransLogger(app)

    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app_logged, '/')

    # Set the configuration of the web server
    cherrypy_config = {
        'engine.autoreload_on': True,
        'log.screen': True,
        'server.socket_port': 5000,
        'server.socket_host': '0.0.0.0'
    }
    if hub_config.get('ssl_enable'):
        cherrypy_config['server.ssl_module'] = 'pyopenssl'
        cherrypy_config[''] = 'pyopenssl'
        cherrypy_config[''] = hub_config.get('ssl_private_key')
        cherrypy_config[''] = hub_config.get('ssl_private_key')

    cherrypy.config.update(cherrypy_config)

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()

def main():
    """ Main. """
    if hub_config.get('ssl_enable'):
        context = SSL.Context(SSL.SSLv23_METHOD)
        context.use_privatekey_file(hub_config.get('ssl_private_key'))
        context.use_certificate_file(hub_config.get('ssl_cert'))
        app.run(host='0.0.0.0',
                ssl_context=context,
                debug=False)
    else:
        app.run(host='0.0.0.0', debug=False)

if __name__ == "__main__":
    run_server()
