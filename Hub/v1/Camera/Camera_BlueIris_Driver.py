"""Spoke restduino driver object."""
import json, urllib2, md5

from Hub.v1.Common.helpers import bool_or_string
from Hub.v1.Camera.Camera_Driver import CameraDriver

def _parse_driver_info(camera_controller):
    """Grab address out of driver_info."""

    driver_info = {'address' : camera_controller.driver_info.get('address'),
                   'username' : camera_controller.driver_info.get('username'),
                   'password' : camera_controller.driver_info.get('password'),
                   'session' : camera_controller.driver_info.get('session')}

    return driver_info

def _login(camera_controller):
    """BlueIris Login."""
    driver_info = _parse_driver_info(camera_controller)

    data = {}
    data['cmd'] = "login"

    result = _send_raw_command(driver_info,
                               json.dumps(data))
    session_id = result['session']

    loginhash = md5.new()
    loginhash.update(driver_info['username'])
    loginhash.update(':')
    loginhash.update(session_id)
    loginhash.update(':')
    loginhash.update(driver_info['password'])
    login_md5 = loginhash.hexdigest()

    data['response'] = login_md5
    data['session'] = session_id
    result = _send_raw_command(driver_info,
                               json.dumps(data))
    if result['result'] == "success":
        camera_controller.driver_info['session'] = session_id
        camera_controller.active = True
        camera_controller.save()
        return True
    else:
        camera_controller.active = False
        camera_controller.save()
        return False

def _send_command (camera_controller, cmd):
    """Send BlueIris command with session_id."""
    driver_info = _parse_driver_info(camera_controller)

    if driver_info.get('session'):
        cmd['session'] = driver_info.get('session')
        ret_info = _send_raw_command(driver_info,
                                     json.dumps(cmd))
        if ret_info.get('result') == 'success':
            return ret_info

    _login(camera_controller)
    cmd['session'] = driver_info.get('session')
    return _send_raw_command(driver_info,
                             json.dumps(cmd))

def _send_raw_command (driver_info, cmd):
    """Send raw BlueIris command."""
    headers = {'content-type' : 'application/json'}
    result = urllib2.Request(driver_info.get('address'), cmd, headers)
    response_stream = urllib2.urlopen(result)
    json_response = response_stream.read()
    return json.loads(json_response)

def _get_cameras(camera_controller):
    """Get all cameras."""
    data = {}
    data['cmd'] = "camlist"
    result = _send_command(camera_controller, data)
    camera_list = {}
    for data in result['data']:
        option_value = data['optionValue']
        if option_value and 'group' not in data:
            camera_list[option_value] = {}
            camera_list[option_value]['on'] = data['isEnabled']
    return camera_list

def _get_camera(camera_controller, camera_name):
    """Get single camera status."""
    pass

def _set_camera(camera_controller, camera_name, key, value):
    """Set camera status."""
    data = {}
    data['cmd'] = "camconfig"
    data['camera'] = camera_name
    if key == 'on':
        data['enable'] = value
        result = _send_command(camera_controller, data)
        return result['result'] == "success"
    elif key == 'alerts':
        return _enable_indoor_alerts(camera_controller, key)
    else:
        return False

def _get_profile(camera_controller):
    """Get current profile of controller."""
    data = {}
    data['cmd'] = "status"
    result = _send_command(camera_controller, data)
    return result['data']['profile']

def _set_profile(camera_controller, new_profile):
    """Set profile of controller."""
    data = {}
    data['cmd'] = "status"
    data['profle'] = new_profile
    _send_command(camera_controller, data)

def _enable_indoor_alerts(camera_controller, setting):
    """Toggle whether alerts are raised for internal camera."""
    profile = int(_get_profile(camera_controller))
    if setting:
        _set_profile(camera_controller, profile | (1 << 2))
    else:
        _set_profile(camera_controller, profile | ~(1 << 2))
    return True

class CameraBlueIrisDriver(CameraDriver):
    """Camera BlueIris driver."""

    def __init__(self):
        pass

    @staticmethod
    def get_cameras(camera_controller):
        """
        Returns nested dictionary of all cameras' status.

        {
        <camera_1> : {"on" : <bool>, "recording": <bool>, "alerts" : <bool>},
        <camera_2> : {"on" : <bool>, "recording": <bool>, "alerts" : <bool>}
        }
        """
        return _get_cameras(camera_controller)

    @staticmethod
    def get_camera(camera_controller, camera_name):
        """
        Returns dictionary of requested camera's status.

        <camera_name> : {"on" : <bool>, "recording": <bool>, "alerts" : <bool>}
        """
        return _get_camera(camera_controller, camera_name)

    @staticmethod
    def set_camera(camera_controller, camera_name, key, value):
        """
        Modify camera configuration/status according to key=value.

        Return True if option is allowed and successful
        Return False if option is not allowed or unsuccessful
        """
        return _set_camera(camera_controller, camera_name, key, value)
