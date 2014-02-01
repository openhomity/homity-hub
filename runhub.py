"""
Launcher for homity-hub
"""
from Hub import APP
from Hub.api import HUB_CONFIG
if HUB_CONFIG.get('ssl_enable'):
    from OpenSSL import SSL

def main():
    """ Main. """
    if HUB_CONFIG.get('ssl_enable'):
        context = SSL.Context(SSL.SSLv23_METHOD)
        context.use_privatekey_file(HUB_CONFIG.get('ssl_private_key'))
        context.use_certificate_file(HUB_CONFIG.get('ssl_cert'))
        APP.run(host='0.0.0.0',
                ssl_context=context,
                debug=False)
    else:
        APP.run(host='0.0.0.0', debug=False)

if __name__ == '__main__':
    main()
