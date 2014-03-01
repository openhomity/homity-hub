"""DB Class For User."""
from couchdb.mapping import TextField
from Hub.v1.Common.base import HomityObject
from uuid import uuid4
from hashlib import sha256

class User(HomityObject):
    """DB Class For User."""
    username = TextField()
    password = TextField()

    def __init__(self, username="", password="", id=None, **values):
        HomityObject.__init__(self, id=None, **values)
        self.username = username
        salt = uuid4().hex
        self.password = (sha256(salt.encode() +
                        password.encode()).hexdigest() +
                        ':' +
                        salt)

    @classmethod
    def get_user(cls,username):
        found, user = cls._find(username=username)
        if found:
            return user
        else:
            return None

    def change_password(self,password):
        salt = uuid4().hex
        self.password = (sha256(salt.encode() +
                        password.encode()).hexdigest() +
                        ':' +
                        salt)



    