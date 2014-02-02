"""Garage driver base class."""
from Hub.v1.Garage.Garage import GarageController

class GarageDriver(object):
    """Base Driver Class for Garages"""

    def __init__(self):
        pass

    def login(self, spoke):
        """Login as needed."""
        pass

    def logout(self, spoke):
        """Logout as needed."""
        pass

    def get_garages(self, garage_controller):
        """
        Return nested dictionary of garage status.

        {
            "G0" : {"open", <bool>,"on": <bool>},
            "G1" : {"open", <bool>,"on": <bool>}
        }
        """
        return False

    def get_garage(self, garage_controller, garage_num):
        """
        Returns dictionary of garage status.

        { "open", <bool>,"on": <bool>}
        """
        return False

    def set_garage(self, garage_controller, garage_num, key, value):
        """
        Modify garage configuration/status according to key=value

        Return True if option is allowed and successful
        Return False if option is not allowed or unsuccessful
        """
        return False
