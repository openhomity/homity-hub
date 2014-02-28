"""Spoke driver object."""

class SpokeDriver(object):
    """Spoke driver object."""

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
    def get_pins(spoke):
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

    @staticmethod
    def get_pin(spoke, pin_num):
        """
        Returns dictionary of requested pin's status.

        "3" : {"digital" : <bool-True>, "output", <bool>, "on": <bool>}
        or -
        "A1" : {"digital" : <bool-False>, "output": <bool>, "value": <int>}
        If digital=True, "on" signifies whether the pin is currently on or off
        If digital=False, an analog value can be retrieved from "value"
        """
        return False

    @staticmethod
    def set_pin(spoke, pin_num, key, value):
        """
        Modify pin configuration/status according to key=value.

        Return True if option is allowed and successful
        Return False if option is not allowed or unsuccessful
        """
        return False

    @staticmethod
    def get_shell_commands(spoke, pin_num):
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
