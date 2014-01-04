from couchdb.mapping import Document, TextField, IntegerField, DateTimeField, BooleanField, ListField, DictField, Mapping
from Hub.v1.Spoke.Spoke import Spoke

class SpokeDriver():
    """
    Returns nested dictionary of all pins' status in format -
    {
    "3" : {"digital" : <bool-True>, "output", <bool>, "on": <bool>}
    "A1" : {"digital" : <bool-False>, "output": <bool>, "value": <int>}
    }
    If digital=True, "on" signifies whether the pin is currently on or off
    If digital=False, an analog value can be retrieved from "value"
    """
    def get_pins(self, spoke):
        return False
    
    """
    Returns dictionary of requested pin's status in format -
    "3" : {"digital" : <bool-True>, "output", <bool>, "on": <bool>}
    or -
    "A1" : {"digital" : <bool-False>, "output": <bool>, "value": <int>}

    If digital=True, "on" signifies whether the pin is currently on or off
    If digital=False, an analog value can be retrieved from "value"
    """    
    def get_pin(self, spoke, pin_num):
        return False
    
    """
    Modify pin configuration/status according to key=value
    Return True if option is allowed and successful
    Return False if option is not allowed or unsuccessful
    """
    def set_pin(self, spoke, pin_num, key, value):
        return False
    
    """
    Cron is used for scheduling status=True|False for digital output pins
    To accomplish this, we need to give cron a shell command to execute when the time comes
    This function should return two commands, one for status=True, one for False, in format
    {
        "True" : <true_command>,
        "False" : <false_command>
    }
    """
    def get_shell_commands(self, spoke, pin_num):
        return False
    
    
