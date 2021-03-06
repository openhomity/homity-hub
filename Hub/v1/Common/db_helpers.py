"""Random helper functions."""

from Hub.api import couch

def get_couch_db(class_type):
    """Return couch_db for object."""
    if class_type == "Spoke":
        return couch['spokes']
    elif class_type == "GarageController":
        return couch['garages']
    elif class_type == "CameraController":
        return couch['cameras']
    elif class_type == "User":
        return couch['users']

