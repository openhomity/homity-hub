"""Initial setup for homityhub."""
import couchdb, argparse
from commands import getstatusoutput
from os.path import exists

from Hub.v1.Common.User import User

def main():
    """ Main."""
    parser = argparse.ArgumentParser(
            prog='homitysetup',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="OpenHomity Hub Setup Tool"
    )
    parser.add_argument("username", help="Username of new Homity Hub user")
    parser.add_argument("password", help="Password of new Homity Hub user")
    parser.add_argument("-c",
                        "--couch",
                        nargs=2,
                        help="Optional Advanced: User & Pass for couchdb")
    args = parser.parse_args()

    new_hub_username = args.username
    new_hub_password = args.password
    if args.couch:
        couchdb_admin_user, couchdb_admin_pass = args.couch

    '''
    Set up CouchDB
    '''
    couch = couchdb.Server(url="http://localhost:5984")
    if args.couch:
        couch.resource.credentials = (couchdb_admin_user, couchdb_admin_pass)

    for db_name in ['users', 'sessions', 'spokes',
                    'garages', 'alarms', 'cameras', 'locks']:
        print 'Creating "%s" database' % db_name
        try:
            couch.create(db_name)
            print '"%s" db created' % db_name
        except couchdb.Unauthorized:
            raise Exception(
                'Unauthorized - specify couchdb user credentials in script')
        except couchdb.PreconditionFailed:
            print '    "%s" db already exists, moving on' % db_name

    hub_user = User.get_user(new_hub_username)
    if hub_user != None:
        print "Updating user %s's password" % new_hub_username
        hub_user.change_password(new_hub_password)
        hub_user.save()
        print ("Successfully updated %s - %s:%s" %
           (hub_user.id, hub_user.username, hub_user.password))
    else:
        print "Creating new user %s" % new_hub_username
        hub_user = User(new_hub_username, new_hub_password)
        hub_user.save()
        print ("Successfully created %s - %s:%s" %
           (hub_user.id, hub_user.username, hub_user.password))

    '''
    Set up config & log files
    '''
    if not exists('/etc/homity/homityhub.conf'):
        print "Copying default.conf to /etc/homity/homityhub.conf"
        try:
            getstatusoutput("cp default.conf /etc/homity/homityhub.conf")
        except:
            raise Exception('Configuration file creation failed - \
                            make sure /etc/homity directory is \
                            created and owned by current user')
        print "Creating log file at /var/log/homity/Hub.log"
    if not exists('/var/log/homity/Hub.log'):
        try:
            getstatusoutput("touch /var/log/homity/Hub.log")
        except:
            raise Exception('Log file creation failed - \
                            make sure /var/log/homity directory \
                            is created and owned by current user')

if __name__ == '__main__':
    main()

