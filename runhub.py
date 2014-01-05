from Hub import app
from Hub.api import hub_config
if hub_config.get('ssl_enable'):
    from OpenSSL import SSL

def main():
    if hub_config.get('ssl_enable'):
        context = SSL.Context(SSL.SSLv23_METHOD)
        context.use_privatekey_file(hub_config.get('ssl_private_key'))
        context.use_certificate_file(hub_config.get('ssl_cert'))
        app.run(host='0.0.0.0',ssl_context=context, debug=False)
    else:
        app.run(host='0.0.0.0', debug=False)

if __name__ == '__main__':
    main()