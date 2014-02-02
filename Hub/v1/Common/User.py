"""DB Class For User."""
from couchdb.mapping import Document, TextField, DictField

class User(Document):
    """DB Class For User."""
    username = TextField()
    password = TextField()
    privilege = TextField()
    driver_data = DictField()


    