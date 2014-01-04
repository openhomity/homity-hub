from flask import Flask

app = Flask(__name__)

import Hub.api

from Hub.v1.api import v1api
app.register_blueprint(v1api)
from Hub.v1.Spoke.spoke_api import v1spoke
app.register_blueprint(v1spoke)


