from Hub.v1.Garage.Garage import GarageController

class GarageDriver():
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
        return False
    
    """
    Returns dictionary of garage status in format -
    { "open", <bool>,"on": <bool>}
    """
    def get_garage(self, garage_controller, garage_num):
        return False
    
    """
    Modify garage configuration/status according to key=value
    Return True if option is allowed and successful
    Return False if option is not allowed or unsuccessful
    """
    def set_garage(self, garage_controller, garage_num, key, value):
        return False
    
    
