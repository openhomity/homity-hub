import json, urllib2

from Hub.v1.Garage.Garage import GarageController
from Hub.v1.Garage.Garage_Driver import GarageDriver
from Hub.v1.Common.helpers import bool_or_string

def _parse_driver_info(garage):
    garage_driver_info = garage.driver_info
    
    driver_info = {}
    driver_info['address'] = garage_driver_info.get('address')
    
    return driver_info

def _get_garages(driver_info):
    return _send_cmd("GAR",driver_info)

def _get_garage(garage_num, driver_info):
    return _send_cmd(garage_num,driver_info)

def _set_garage(garage_num, key, value, driver_info):
    value = bool_or_string(value)
    garage_status = _get_garage(garage_num, driver_info)
    
    if key == 'open' and value in [True,False]:
        if garage_status.get('open') == (not value):
            return _garage_toggle(garage_num,driver_info)
            
    elif key == 'on' and value in [True,False]:
        return _set_garage_power(garage_num,value,driver_info)
    
    else:
        return False

def _garage_toggle(garage_num, driver_info):
    return _send_cmd(str(garage_num) + "/TOG", driver_info)

def _set_garage_power(garage_num, new_status, driver_info):
    if new_status:
        new_status = "ON"
    else:
        new_status = "OFF"
    return _send_cmd(str(garage_num) + "/" + new_status, driver_info)
    
def _send_cmd(cmd,driver_info):
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

class GarageRestDuinoDriver(GarageDriver):
    """
    Login/Logout functions as needed.
    """
    def login(self, spoke):
        pass
    
    def logout(self, spoke):
        pass
    
    """
    Returns nested dictionary of garage status in format -
    {
        "G0" : {"open", <bool>,"on": <bool>},
        "G1" : {"open", <bool>,"on": <bool>}
    }
    """
    def get_garages(self, garage_controller):
        return _get_garages(_parse_driver_info(garage_controller))
    
    """
    Returns dictionary of garage status in format -
    { "open", <bool>,"on": <bool>}
    """
    def get_garage(self, garage_controller, garage_num):
        return _get_garage(garage_num,_parse_driver_info(garage_controller))
    
        """
    Modify garage configuration/status according to key=value
    Return True if option is allowed and successful
    Return False if option is not allowed or unsuccessful
    """
    def set_garage(self, garage_controller, garage_num, key, value):
        return _set_garage(garage_num,key,value,_parse_driver_info(garage_controller))
    

    
