from couchdb.mapping import Document, TextField, IntegerField, DateTimeField, BooleanField, ListField, DictField, Mapping
import datetime

class Session(Document):
    sessionid = TextField()
    user = TextField()
    privilege = TextField()
    active = BooleanField()
    established = DateTimeField(default=datetime.datetime.now())
    remoteAddress = TextField()
    