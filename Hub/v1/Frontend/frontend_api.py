"""
TBD
"""
from flask import Blueprint, request, make_response
import json

from Hub.v1.Common.auth import requires_auth


V1FRONTEND = Blueprint('V1FRONTEND', __name__)

@V1FRONTEND.route('/', methods=['GET'])
@requires_auth
def get_all_status():
    """Placeholder for root get."""
    return app.send_static_file('index.html')