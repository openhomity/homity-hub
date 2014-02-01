"""Spoke driver object."""
from Hub.v1.Spoke.Spoke import Spoke

class SpokeDriver(object):
    """Spoke driver object."""

    def __init__(self):
        pass

    def login(self, spoke):
        """Login as needed."""
        pass

    def logout(self, spoke):
        """Logout as needed."""
        pass

    def get_pins(self, spoke):
        """
        Returns nested dictionary of all pins' status.

        {
        "3" : {"digital" : <bool-True>, "output", <bool>, "on": <bool>}
        "A1" : {"digital" : <bool-False>, "output": <bool>, "value": <int>}
        }
        If digital=True, "on" signifies whether the pin is currently on or off
        If digital=False, an analog value can be retrieved from "value"
        """
        return False

    def get_pin(self, spoke, pin_num):
        """
        Returns dictionary of requested pin's status.

        "3" : {"digital" : <bool-True>, "output", <bool>, "on": <bool>}
        or -
        "A1" : {"digital" : <bool-False>, "output": <bool>, "value": <int>}
        If digital=True, "on" signifies whether the pin is currently on or off
        If digital=False, an analog value can be retrieved from "value"
        """
        return False

    def set_pin(self, spoke, pin_num, key, value):
        """
        Modify pin configuration/status according to key=value.

        Return True if option is allowed and successful
        Return False if option is not allowed or unsuccessful
        """
        return False

    def get_shell_commands(self, spoke, pin_num):
        """
        Return shell commands for turning pins on/off.

        Cron is used for scheduling status=True|False
        This function should return two commands,
        one for status=True, one for False, in format
        {
            "True" : <true_command>,
            "False" : <false_command>
        }
        """
        return False
