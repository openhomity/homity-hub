"""
Flask API Blueprint for camera v1

A "camera controller" is any object that has one or more "cameras",
where a camera has the following properties -
- on : <bool>
- recording : <bool>
- alerts : <bool>

Allows for POST command to create new camera controller objects,
as well as PUT to modify and GET to view

Camera v1 implements a driver architecture,
importing pluggable drivers from the Hub/v1/Camera directory
All spoke drivers should super the CameraDriver class and implement its methods
"""
from flask import Blueprint, request, make_response
import json

from Hub.v1.Common.auth import requires_auth
from Hub.v1.Common.helpers import int_or_string, bool_or_string

from Hub.v1.Camera.Camera import CameraController, CAMERA_DRIVERS


V1CAMERA = Blueprint('V1CAMERA', __name__)

@V1CAMERA.route('/v1/cameracontroller', methods=['POST'])
@requires_auth
def new_camera_controller():
    """
    Create new spoke from input dictionary -

    {'name': <string>, 'driver': <string>, 'driver_info': <dict>}
    """

    camera_controller_info = request.get_json(silent=True, cache=True)
    camera_controller = CameraController(**camera_controller_info)
    camera_controller.refresh()

    return _camera_controllers_internal(
        camera_controller_id=camera_controller.id)

@V1CAMERA.route('/v1/cameradrivers', methods=['GET'])
@requires_auth
def get_spoke_drivers():
    """Return list of camera drivers."""
    return json.dumps(CAMERA_DRIVERS)

@V1CAMERA.route('/v1/cameracontroller', methods=['GET'])
@requires_auth
def get_spokes():
    """Get all camera controllers."""
    return _camera_controllers_internal()

@V1CAMERA.route('/v1/cameracontroller/<path:path>', methods=['GET', 'PUT'])
@requires_auth
def get_camera_controller_path(path):
    """Parse nested camera controller path along with optional value parameter for PUTs."""
    parsed_path = path.split("/")
    path = map(int_or_string,
               parsed_path)

    if request.method == 'PUT':
        try:
            value = request.args['value']
        except KeyError:
            value = None
    else:
        value = None

    if len(path) > 1:
        return _camera_controllers_internal(camera_controller_id=path[0],
                                path=path[1:],
                                value=value)
    elif len(path) == 1:
        return _camera_controllers_internal(camera_controller_id=path[0],
                                value=value)
    else:
        return _camera_controllers_internal()

@V1CAMERA.route('/v1/cameracontroller/<path:path>', methods=['DELETE'])
@requires_auth
def delete_camera_controller(path):
    """Handle camera controller-related deletion."""
    parsed_path = path.split("/")
    parsed_path = map(int_or_string,
                      parsed_path)

    camera_controller_id = parsed_path[0]
    if len(parsed_path) == 1: #delete a camera controller
        camera_controller = CameraController.get_id(camera_controller_id)
        if camera_controller:
            camera_controller.delete()
            return ""

    return make_response(json.dumps({"reason" : "InvalidPath"}),
                         404)

def _camera_controllers_internal(camera_controller_id=None, path=None, value=None):
    """
    Process GET/PUT requests for camera controller

    Level indicates level past /cameracontroller/ in the URI
    Return list of camera controllers if no camera_controller_id given
    If GET, return specific field asked for by id & path
    If SET, try to set object described by path to value
    Only specific sets are allowed, enforced either here or at the driver
    InvalidInput strings are a trick to help see where we fell.
    """

    if camera_controller_id == None:
        if value != None:
            return make_response(json.dumps({"reason" : "NotImplemented"}),
                                 501)
        camera_controller_list = CameraController.list(dict_format=True)
        return json.dumps(camera_controller_list)
    else:
        camera_controller = CameraController.get_id(camera_controller_id)
        if not camera_controller:
            return make_response(json.dumps({"reason" : "InvalidSpokeID"}),
                                 404)

        camera_controller_dict = camera_controller.dict()

        return_value = camera_controller_dict

        if path == None:
            path = []
        path_len = len(path)

        #Walk the spoke's status dictionary until we get to the end of the path,
        #throw 404 if any key doesn't exist
        if value == None:
            for level in path:
                try:
                    return_value = return_value[level]
                except (KeyError, IndexError):
                    return make_response(json.dumps(
                        {"reason" : "BadGetPath-%s" % level}),
                        404)
            return json.dumps(return_value)

        else:
            value = bool_or_string(value)
            if path_len == 3:
                #Setting a camera's value - e.g.
                #/cameracontroller/<id>/cameras/<camera_id>/<key> = value
                if (path[0] == "cameras" and
                    path[1] in list(camera_controller.cameras)):
                    if path[2] in ["name", "allocated"]:
                        camera_controller.cameras[path[1]][path[2]] = value
                        camera_controller.save()
                        return json.dumps(
                            camera_controller.cameras[path[1]][path[2]])
                    elif (camera_controller.driver_class.set_camera(
                                    camera_controller,
                                    camera_controller[path[1]]['name'],
                                    path[2],
                                    value)):
                        #Let the driver decide if it can handle it
                        camera_controller.refresh()
                        return json.dumps(camera_controller.dict())
                    else:
                        return make_response(json.dumps(
                            {"reason" : "NotImplementedPut3"}),
                            501)
                else:
                    return make_response(
                        json.dumps({"reason" : "InvalidInputPut3"}),
                        404)
            elif path_len == 2:
                #Setting driver_info - e.g.
                #/cameracontroller/<id>/driver_info/<key> = value
                if path[0] == "driver_info":
                    camera_controller.driver_info[path[1]] = value
                else:
                    return make_response(json.dumps(
                        {"reason" : "NotImplementedPut2"}),
                        501)
                camera_controller.save()
                camera_controller_dict = camera_controller.dict()
                return json.dumps(camera_controller_dict[path[0]][path[1]])
            elif path_len == 1:
                #Changing a spoke top-level setting - e.g.
                #/cameracontroller/<id>/<key> = value
                if path[0] in ["name", "driver"]:
                    setattr(camera_controller, path[0], value)
                else:
                    return make_response(json.dumps(
                        {"reason" : "NotImplementedPut1"}),
                        501)
                camera_controller.save()
                camera_controller_dict = camera_controller.dict()
                return json.dumps(camera_controller_dict[path[0]])
            else:
                return make_response(json.dumps(
                    {"reason" : "NotImplementedPut0"}),
                    501)

    return make_response(json.dumps({"reason" : "InvalidInputBottom"}),
                         404)

@V1CAMERA.route('/v1/camera', methods=['GET'])
@requires_auth
def get_cameras():
    """Get all 'allocated' cameras."""
    return _cameras_internal()

@V1CAMERA.route('/v1/camera/<path:path>', methods=['GET', 'PUT'])
@requires_auth
def get_camera_path(path):
    """Parse nested camera path along with optional value parameter for PUTs."""
    parsed_path = path.split("/")
    path = map(int_or_string,
               parsed_path)

    if request.method == 'PUT':
        try:
            value = request.args['value']
        except KeyError:
            value = None
    else:
        value = None

    if len(path) > 1:
        return _cameras_internal(camera_id=path[0],
                              path=path[1:],
                              value=value)
    elif len(path) == 1:
        return _cameras_internal(camera_id=path[0],
                              value=value)
    else:
        return _cameras_internal()

def _cameras_internal(camera_id=None, path=None, value=None):
    """
    Process GET/PUT requests for camera.

    Path is a list indicating levels past /camera/ in the URI
    Only retrieves pins marked 'allocated' unless specific camera_id is given
    If camera_id, processed same as /cameracontroller/<id>/cameras/<camera_id>
    """

    if camera_id == None:
        #Return list of all allocated cameras
        if value != None:
            return make_response(json.dumps({"reason" : "InvalidInput"}),
                                 501)
        camera_list = CameraController.list_available_cameras()
        return json.dumps(camera_list)
    else:
        #Grab only the object requested
        #Find the spoke that has this pin and pass it off to the spoke handler

        if path == None:
            path = []

        camera_controller = CameraController.get_for_camera_id(camera_id)
        return _camera_controllers_internal(
            camera_controller_id=camera_controller.id,
            path=["cameras", camera_id] + path,
            value=value)

    return make_response(json.dumps({"reason" : "PinNotFound"}),
                         404)

