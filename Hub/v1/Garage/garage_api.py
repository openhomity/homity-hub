"""
Flask API Blueprint for Garage v1

A "garage controller" is any object that has one or more "garages",
where each garage is an independant door with these properties -
- "open" : <status of garage - True if open, False if closed>
- "on" :  <power status of door, True if turned on, False if turned off

Allows for POST command to create new garage controller objects,
as PUT to modify and GET to view

Garage v1 implements a driver architecture, importing pluggable
drivers from the Server/v1/Garage directory
All garage drivers should super the GarageDriver class and implement its methods
"""
from flask import Blueprint, request, make_response
import json
from sys import modules

from Hub.api import couch
from Hub.v1.Common.auth import requires_auth
from Hub.v1.Common.helpers import int_or_string, bool_or_string

from Hub.v1.Garage.Garage import GarageController
from Hub.v1.Garage.Garage_Driver import GarageDriver
from Hub.v1.Garage.Garage_RestDuino_Driver import GarageRestDuinoDriver


V1GARAGE = Blueprint('V1GARAGE', __name__)

GARAGE_CONTROLLER_DRIVERS = [
    "GarageRestDuinoDriver"
]

def _driver_name_to_class(driver_name):
    """
    Convert garage.driver string to driver's class.

    If not found, return generic GarageDriver()
    """
    if driver_name in GARAGE_CONTROLLER_DRIVERS:
        try:
            return reduce(getattr,
                          driver_name.split("."),
                          modules[__name__])()
        except AttributeError:
            return GarageDriver()
    return GarageDriver()

#Call driver's method to query garage status
#Pass return dictionary to garage_controller object to process update
#If garage_controller doesn't respond, mark active = False
def _update_garage_status(garage_controller):
    """
    Call driver's method to query garage status.

    Pass return dictionary to garage_controller object to process update
    If garage_controller doesn't respond, mark active = False
    """
    driver = _driver_name_to_class(garage_controller.driver)
    garages = driver.get_garages(garage_controller)
    if garages:
        garage_controller.active = True
        garage_controller.update_garages(garages)
    else:
        garage_controller.active = False
    return garage_controller


@V1GARAGE.route('/v1/garagecontroller', methods=['POST'])
@requires_auth
def new_garage_controller():
    """
    Create new garage_controller from input dictionary.

    {'name': <string>, 'driver': <string>, 'driver_info': <dict>}
    """
    garage_db = couch['garages']

    garage_controller_info = request.get_json(silent=True,
                                              cache=True)
    garage_controller = GarageController(
        name=garage_controller_info.get('name'),
        driver=garage_controller_info.get('driver'),
        active=False,
        garages={},
        driver_info=garage_controller_info.get('driver_info'))

    garage_controller = _update_garage_status(garage_controller)
    garage_controller.store(garage_db)

    return _garage_controllers_internal(
        garage_controller_id=garage_controller.id)

@V1GARAGE.route('/v1/garagecontrollerdrivers', methods=['GET'])
@requires_auth
def get_garage_controller_drivers():
    """
    Return list of garage controller drivers.
    """
    return json.dumps(GARAGE_CONTROLLER_DRIVERS)


@V1GARAGE.route('/v1/garagecontroller', methods=['GET'])
@requires_auth
def get_garage_controllers():
    """
    Get all garage controllers.
    """
    return _garage_controllers_internal()

@V1GARAGE.route('/v1/garagecontroller/<path:path>', methods=['GET', 'PUT'])
@requires_auth
def get_garage_controller_path(path):
    """
    Parse nested garage controller path along with optional value.
    """
    parsed_path = path.split("/")
    path = map(int_or_string,
               parsed_path)

    if request.method == 'PUT':
        try:
            value = request.args['value']
        except KeyError:
            value = False
    else:
        value = False

    if len(path) > 1:
        return _garage_controllers_internal(garage_controller_id=path[0],
                                            path=path[1:],
                                            value=value)
    elif len(path) == 1:
        return _garage_controllers_internal(garage_controller_id=path[0],
                                            value=value)
    else:
        return _garage_controllers_internal()

@V1GARAGE.route('/v1/garagecontroller/<path:path>', methods=['DELETE'])
@requires_auth
def delete_garage_controller(path):
    """
    Handle garage controller-related deletion.
    """
    garage_db = couch['garages']
    parsed_path = path.split("/")
    parsed_path = map(int_or_string,
                      parsed_path)
    garage_controller_id = parsed_path[0]
    if len(parsed_path) == 1: #delete a garage controller
        if garage_controller_id in garage_db:
            del garage_db[garage_controller_id]
            return ""

    return make_response(json.dumps({"reason" : "InvalidPath"}),
                         404)


def _garage_controllers_internal(
    garage_controller_id="", path=None, value=False):
    """
    Process GET/PUT requests for garage controller.

    Level indicates level past /garagecontroller/ in the URI
    Return list of garage controllers if no garage_controller_id given
    If GET, return specific field asked for by garage_controller_id & path
    If SET, try to set object described by path to value
    Only specific sets are allowed, enforced either here or at the driver
    InvalidInput strings are a trick to help see where we fell
    """
    garage_db = couch['garages']

    if path == None:
        path = []

    path_len = len(path)
    garage_controller_list = []
    garage_controller = GarageController()
    if not garage_controller_id:
        if value:
            return make_response(json.dumps({"reason" : "NotImplemented"}),
                                 501)
        for garage_id in garage_db:
            garage_controller = GarageController.load(garage_db,
                                                      garage_id)
            garage_controller = _update_garage_status(garage_controller)
            garage_controller.store(garage_db)
            garage_controller_list.append(garage_controller.status())
        return json.dumps(garage_controller_list)
    else:
        if garage_controller_id not in garage_db:
            return make_response(
                json.dumps({"reason" : "InvalidGarageControllerID"}),
                404)
        garage_controller = GarageController.load(garage_db,
                                                  garage_controller_id)
        garage_controller = _update_garage_status(garage_controller)
        garage_controller.store(garage_db)
        garage_controller_dict = garage_controller.status()

        return_value = garage_controller_dict

        """
        Walk the garage controller's status dictionary until we get to
        the end of the path, throw 404 if any key doesn't exist
        """
        if not value:
            for level in path:
                try:
                    return_value = return_value[level]
                except KeyError:
                    return make_response(
                        json.dumps({"reason" : "BadGetKey-%s" % level}),
                        404)
                except IndexError:
                    return make_response(
                        json.dumps({"reason" : "BadGetIndex-%s" % level}),
                        404)
            return json.dumps(return_value)

        else:
            value = bool_or_string(value)
            driver = _driver_name_to_class(garage_controller.driver)
            if path_len == 3:
                """
                Setting a garage's value - e.g.
                /garagecontroller/<controller_id>/garages/<garage_id>/<key>
                value=<new_value>
                """
                if (path[0] == "garages" and
                    path[1] in list(garage_controller.garages)):
                    if path[2] in ["name", "allocated"]:
                        garage_controller.garages[path[1]][path[2]] = value
                        garage_controller.store(garage_db)
                        return json.dumps(value)
                    elif path[2] in ["open", "on"]:
                        if driver.set_garage(
                                garage_controller,
                                garage_controller.garages[path[1]]['num'],
                                path[2],
                                value):
                            garage_controller = _update_garage_status(
                                garage_controller)
                            garage_controller.store(garage_db)
                            return json.dumps(value)
                        else:
                            make_response(json.dumps({"reason" : "PutError3"}),
                                          500)
                    return make_response(
                        json.dumps({"reason" : "NotImplementedPut3"}),
                        501)
                else:
                    return make_response(
                        json.dumps({"reason" : "InvalidInputPut3"}),
                        404)
            elif path_len == 2:
                """
                Setting driver_info - e.g.
                /garagecontroller/<garage_controller_id>/driver_info/<key>
                value=<new_value>
                """
                if path[0] == "driver_info":
                    garage_controller.driver_info[path[1]] = value
                else:
                    return make_response(
                        json.dumps({"reason" : "NotImplementedPut2"}),
                        501)
                garage_controller.store(garage_db)
                garage_controller_dict = garage_controller.status()
                return json.dumps(garage_controller_dict[path[0]][path[1]])
            elif path_len == 1:
                """
                Changing a garage controller top-level setting - e.g.
                /garagecontroller/<garage_controller_id>/<key> = value
                """
                if path[0] == "name":
                    garage_controller.name = value
                elif path[0] == "driver":
                    garage_controller.driver = value
                else:
                    return make_response(
                        json.dumps({"reason" : "NotImplementedPut1"}),
                        501)
                garage_controller.store(garage_db)
                garage_controller_dict = garage_controller.status()
                return json.dumps(garage_controller_dict[path[0]])
            else:
                return make_response(
                    json.dumps({"reason" : "NotImplementedPut0"}),
                    501)

    return make_response(
        json.dumps({"reason" : "InvalidInputBottom"}),
        404)

@V1GARAGE.route('/v1/garage', methods=['GET'])
@requires_auth
def get_garages():
    """
    Get all 'allocated' garages.
    """
    return _garages_internal()


@V1GARAGE.route('/v1/garage/<path:path>', methods=['GET', 'PUT'])
@requires_auth
def get_garages_path(path):
    """
    Parse nested garage path along with optional value parameter for PUTs.
    """
    parsed_path = path.split("/")
    path = map(int_or_string,
               parsed_path)

    if request.method == 'PUT':
        try:
            value = request.args['value']
        except KeyError:
            value = False
    else:
        value = False

    if len(path) > 1:
        return _garages_internal(garage_id=path[0],
                                 path=path[1:],
                                 value=value)
    elif len(path) == 1:
        return _garages_internal(garage_id=path[0],
                                 value=value)
    else:
        return _garages_internal()


def _garages_internal(garage_id="", path=None, value=False):
    """
    Process GET/PUT requests for garage

    Path is a list indicating levels past /garage/ in the URI
    Only retrieves garages marked 'allocated' unless specific garage_id is given
    If garage_id, request processed same as
    /garagecontroller/<garage_controller_id>/garages/<garage_id>
    """
    garage_db = couch['garages']

    if path == None:
        path = []

    garage_list = []
    garage_controller = GarageController()
    if not garage_id:
        #Return list of all allocated garages
        if value:
            return make_response(
                json.dumps({"reason" : "InvalidInput"}),
                501)
        for garage_id in garage_db:
            garage_controller = GarageController.load(garage_db,
                                                      garage_id)
            garage_controller = _update_garage_status(garage_controller)
            garage_controller.store(garage_db)
            if garage_controller['active']:
                for garage_id, garage in garage_controller.garages.items():
                    if garage.get('allocated'):
                        garage_list.append(garage)
        return json.dumps(garage_list)
    else:
        """
        Grab only the object requested
        Find the garage controller that houses this garage
        and pass it off to the garage controller handler
        """
        for garage_controller_entry in garage_db:
            garage_controller = GarageController.load(garage_db,
                                                      garage_controller_entry)
            if (garage_controller.active and
                garage_id in list(garage_controller.garages)):
                return _garage_controllers_internal(
                    garage_controller_id=garage_controller_entry,
                    path=["garages", garage_id] + path,
                    value=value)

    return make_response(
        json.dumps({"reason" : "GarageNotFound"}),
        404)

