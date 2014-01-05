#from ConfigParser import SafeConfigParser, NoOptionError
import couchdb
from Hub.v1.Common.User import User
import argparse
from commands import getstatusoutput

def main():
    parser = argparse.ArgumentParser(
            prog='homitysetup',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="OpenHomity Hub Setup Tool"
    )
    parser.add_argument("username", help="Username of new Homity Hub user")
    parser.add_argument("password", help="Password of new Homity Hub user")
    parser.add_argument("-c", "--couch", nargs=2, help="Optional Advanced: Username & Password for couchdb")
    args = parser.parse_args()
    
    new_hub_username = args.username
    new_hub_password = args.password
    couchdb_admin_user, couchdb_admin_pass = args.couch
    
    '''
    Set up CouchDB
    '''
    couch = couchdb.Server(url="http://localhost:5984")
    if couchdb_admin_user:
        couch.resource.credentials = (couchdb_admin_user, couchdb_admin_pass)
        
    for db_name in ['users','sessions','spokes','garages','alarms','cameras','locks']:
        print 'Creating "%s" database' % db_name
        try:
            couch.create(db_name)
            print '"%s" db created' % db_name
        except couchdb.Unauthorized:
            raise Exception('Unauthorized - edit this script to specify couchdb admin user credentials')
        except couchdb.PreconditionFailed:
            print '    "%s" db already exists, moving on' % db_name
    
    print "Creating new user %s" % new_hub_username
    user_db = couch['users']
    new_user = User()
    new_user.username = new_hub_username
    password = new_hub_password
    ohomeuser.privilege = 'user'
    salt = uuid.uuid4().hex
    new_user.password = hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

    new_user.store(user_db)
    print "Successfully created %s:%s" % (new_user.username, new_user.password)

    '''
    Set up config & log files
    '''
    try:
        getstatusoutput("cp default.conf /etc/homity/homityhub.conf")
    except:
        raise Exception('Configuration file creation failed - make sure /etc/homity directory is created and owned by current user')
    
    try:
        getstatusoutput("touch /var/log/homity/Hub.log")
    except:
        raise Exception('Log file creation failed - make sure /var/log/homity directory is created and owned by current user')

    
if __name__ == '__main__':
    main()
    
