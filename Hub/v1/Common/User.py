"""DB Class For User."""
from couchdb.mapping import TextField
from Hub.v1.Common.base import HomityObject
from uuid import uuid4
from hashlib import sha256

class User(HomityObject):
    """DB Class For User."""
    password = TextField()

    def __init__(self, username=None, password="", **values):
        HomityObject.__init__(self, id=username, **values)
        salt = uuid4().hex
        self.password = (sha256(salt.encode() +
                        password.encode()).hexdigest() +
                        ':' +
                        salt)

    @classmethod
    def get_user(cls, username):
        """Fetch user object by username."""
        return cls.get_id(username)

    def change_password(self, password):
        """Change user's PW to password."""
        salt = uuid4().hex
        self.password = (sha256(salt.encode() +
                        password.encode()).hexdigest() +
                        ':' +
                        salt)

    def check_password(self, password):
        """Check if user password is == to password."""
        dbpasswordhash, salt = self.password.split(':')
        userpasswordhash = sha256(salt.encode() +
                                  password.encode()).hexdigest()
        return userpasswordhash == dbpasswordhash



    