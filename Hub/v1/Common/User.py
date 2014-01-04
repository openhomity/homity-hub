from couchdb.mapping import Document, TextField, IntegerField, DateTimeField, BooleanField, ListField, DictField, Mapping
from datetime import datetime

class User(Document):
    username = TextField()
    password = TextField()
    privilege = TextField()
    alarmSLT = TextField()

    