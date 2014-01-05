from couchdb.mapping import Document, TextField

class User(Document):
    username = TextField()
    password = TextField()
    privilege = TextField()
    alarmSLT = TextField()

    