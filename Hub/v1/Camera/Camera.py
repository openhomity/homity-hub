"""Spoke controller object."""
from couchdb.mapping import TextField, BooleanField, DictField
from uuid import uuid4

from Hub.v1.Common.helpers import update_crontab
from Hub.v1.Common.base import HomityObject

from Hub.api import couch
from sys import modules
from Hub.v1.Camera.Camera_Driver import CameraDriver
from Hub.v1.Camera.Camera_BlueIris_Driver import CameraBlueIrisDriver

CAMERA_DRIVERS = [
    "CameraBlueIrisDriver"
]

def _driver_name_to_class(driver_name):
    """
    Convert CAMERA_DRIVERS string to driver's class

    If not found, return generic CameraDriver()
    """
    if driver_name in CAMERA_DRIVERS:
        try:
            return reduce(getattr, driver_name.split("."), modules[__name__])()
        except AttributeError:
            return CameraDriver()
    return CameraDriver()

class CameraController(HomityObject):
    """
    Camera controller object.
    "name" : <name of camera controller>
    "active" : <true|false if controller is online>
    "driver" : <name of driver>
    "driver_info" : <dict containing driver-specific info>
    "cameras" :
        {
        "camera_id" : {
            "id" : <uuid of camera>
            "name" : <name of camera>
            "allocated" : <True if camera is being used>
            "on" : <True|False if camera is powered on>
            "recording" : <True|False if camera is recording>
            "alerts" : <True|False if motion alerts>
        }
        }"""
    name = TextField()
    active = BooleanField()
    driver = TextField()
    driver_info = DictField()
    cameras = DictField()

    def __init__(self, id=None, **values):
        HomityObject.__init__(self, id, **values)
        self.driver_class = _driver_name_to_class(self.driver)

    @classmethod
    def list(cls,dict_format=False):
        return cls._list(dict_format)

    @classmethod
    def list_available_cameras(cls):
        return cls._find_all_subobjects('cameras', allocated=True)

    @classmethod
    def get_for_camera_id(cls, camera_id):
        """Get the camera controller containing camera_id."""
        found, camera_controller = cls._find_in_list(camera=camera_id)
        if found:
            return camera_controller
        else:
            return None

    def delete(self):
        """Delete camera controller."""
        del self.class_db[self.id]

    def _add_camera(self, camera):
        """Add new pin to object."""
        camera_id = uuid4().hex
        self.cameras[camera_id] = {
            'allocated' : False,
            'id' : camera_id,
            'name' : camera.get('name'),
            'description' : camera.get('description'),
            'on' : camera.get('on'),
            'recording' : camera.get('recording'),
            'alerts' : camera.get('alerts'),
            'controller' : self.id,
            'location' : self.name
            }

    def refresh(self):
        """Update object according to what we get from driver."""
        self.driver_class = _driver_name_to_class(self.driver)
        camera_status = self.driver_class.get_cameras(self)
        if not camera_status:
            pass
        else:
            existing_camera_names_to_ids = ({item.get('name'):item.get('id') for
                                         item in self.cameras.values()})
            for camera in camera_status:
                if camera.get('name') in list(existing_camera_names_to_ids):
                    camera_id = existing_camera_names_to_ids.get(
                        camera.get('name'))
                    self.cameras[camera_id]['on'] = camera.get('on')
                    self.cameras[camera_id]['recording'] = camera.get(
                        'recording')
                    self.cameras[camera_id]['alerts'] = camera.get('alerts')
                    self.cameras[camera_id]['location'] = self.name
                    self.cameras[camera_id]['controller'] = self.id
                else:
                    self._add_camera(camera)
        self.save()
