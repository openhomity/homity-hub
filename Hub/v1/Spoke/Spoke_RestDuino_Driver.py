"""Spoke restduino driver object."""
import json, urllib2

from Hub.v1.Common.helpers import bool_or_string

def _parse_driver_info(spoke):
    """Grab duino address out of driver_info."""
    spoke_driver_info = spoke.driver_info

    driver_info = {}
    driver_info['address'] = spoke_driver_info.get('address')

    return driver_info

def _get_pins(driver_info):
    """Get all pins status."""
    return _send_cmd("",
                     driver_info)

def _get_pin(pin_num, driver_info):
    """Get single pin status."""
    return _send_cmd(pin_num,
                     driver_info)

def _set_pin(pin_num, key, value, driver_info):
    """Set single pin status."""
    value = bool_or_string(value)
    pin_status = _get_pin(pin_num,
                          driver_info)

    if pin_status.get('digital'):
        if (key == 'output' and
            value in [True, False]):
            return _set_pin_output(pin_num,
                                   value,
                                   driver_info)

        elif (key == 'status' and
              value in [True, False] and
              pin_status.get('output')):
            return _enable_pin(pin_num, value, driver_info)

    return False

def _set_pin_output(pin_num, output, driver_info):
    """Set pin mode to output|input."""
    if output:
        new_status = "OUT"
    else:
        new_status = "IN"
    return _send_cmd(str(pin_num) + "/" + new_status, driver_info)

def _enable_pin(pin_num, do_enable, driver_info):
    """Turn a pin on."""
    if do_enable:
        new_status = "HIGH"
    else:
        new_status = "LOW"
    return _send_cmd(str(pin_num) + "/" + new_status, driver_info)

def _send_cmd(cmd, driver_info):
    """Send raw command to duino."""
    result = urllib2.Request(driver_info.get('address')+cmd)
    try:
        response_stream = urllib2.urlopen(result, timeout=1)
    except urllib2.URLError:
        return False
    json_response = response_stream.read()
    if json_response:
        return json.loads(json_response)
    else:
        return True

def _get_shell_commands(pin_num, driver_info):
    """Return shell commands for pin on|off."""
    shell_commands = {}
    shell_commands['True'] = ("wget -O /dev/null %s%s/%s" %
                              (driver_info.get('address'),
                               pin_num,
                               "HIGH"))
    shell_commands['False'] = ("wget -O /dev/null %s%s/%s" %
                               (driver_info.get('address'),
                                pin_num,
                                "LOW"))
    return shell_commands

class SpokeRestDuinoDriver(object):
    """Spoke restduino driver object."""

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
        return _get_pins(_parse_driver_info(spoke))

    def get_pin(self, spoke, pin_num):
        """
        Returns dictionary of requested pin's status.

        "3" : {"digital" : <bool-True>, "output", <bool>, "on": <bool>}
        or -
        "A1" : {"digital" : <bool-False>, "output": <bool>, "value": <int>}
        If digital=True, "on" signifies whether the pin is currently on or off
        If digital=False, an analog value can be retrieved from "value"
        """
        return _get_pin(pin_num,
                        _parse_driver_info(spoke))

    def set_pin(self, spoke, pin_num, key, value):
        """
        Modify pin configuration/status according to key=value.

        Return True if option is allowed and successful
        Return False if option is not allowed or unsuccessful
        """
        return _set_pin(pin_num,
                        key,
                        value,
                        _parse_driver_info(spoke))

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
        return _get_shell_commands(pin_num,
                                   _parse_driver_info(spoke))
