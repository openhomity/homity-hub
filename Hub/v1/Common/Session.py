"""DB Class for authenticated session."""
from couchdb.mapping import Document, TextField, DateTimeField, BooleanField
import datetime

class Session(Document):
    """DB Class for authenticated session."""
    sessionid = TextField()
    user = TextField()
    privilege = TextField()
    active = BooleanField()
    established = DateTimeField(default=datetime.datetime.now())
    remoteAddress = TextField()
    