"""Camera driver object."""

class CameraDriver(object):
    """Spoke driver object."""

    def __init__(self):
        pass

    @staticmethod
    def get_cameras(camera_controller):
        """
        Returns nested dictionary of all cameras' status.

        {
        <camera_name> : {"on" : <bool>, "recording", <bool>},
        <camera_name2> : {"on" : <bool>, "recording", <bool>},
        }
        """
        return None

    @staticmethod
    def get_camera(camera_controller, camera_name):
        """
        Returns dictionary of requested camera's status.

        <camera_name> : {"on" : <bool>, "recording", <bool>}
        """
        return None

    @staticmethod
    def set_camera(camera_controller, camera_name, key, value):
        """
        Modify camera configuration/status according to key=value.

        Return True if option is allowed and successful
        Return False if option is not allowed or unsuccessful
        """
        return False
