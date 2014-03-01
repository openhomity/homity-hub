"""
Create Flask app, register blueprints.
"""
from flask import Flask

app = Flask(__name__)

import Hub.api

'''
from Hub.v1.api import V1API
app.register_blueprint(V1API)
'''
from Hub.v1.Spoke.spoke_api import V1SPOKE
app.register_blueprint(V1SPOKE)
from Hub.v1.Garage.garage_api import V1GARAGE
app.register_blueprint(V1GARAGE)
from Hub.v1.Camera.camera_api import V1CAMERA
app.register_blueprint(V1CAMERA)


