"""Garage driver base class."""

class GarageDriver(object):
    """Base Driver Class for Garages"""

    def __init__(self):
        pass

    @staticmethod
    def login(spoke):
        """Login as needed."""
        pass

    @staticmethod
    def logout(spoke):
        """Logout as needed."""
        pass

    @staticmethod
    def get_garages(garage_controller):
        """
        Return nested dictionary of garage status.

        {
            "G0" : {"open", <bool>,"on": <bool>},
            "G1" : {"open", <bool>,"on": <bool>}
        }
        """
        return False

    @staticmethod
    def get_garage(garage_controller, garage_num):
        """
        Returns dictionary of garage status.

        { "open", <bool>,"on": <bool>}
        """
        return False

    @staticmethod
    def set_garage(garage_controller, garage_num, key, value):
        """
        Modify garage configuration/status according to key=value

        Return True if option is allowed and successful
        Return False if option is not allowed or unsuccessful
        """
        return False
