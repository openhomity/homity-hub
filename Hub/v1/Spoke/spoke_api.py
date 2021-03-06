"""
Flask API Blueprint for spoke v1

A "spoke" is any object that has one or more "pins",
where a pin has the following properties -
- output :
- digital :

Allows for POST command to create new spoke objects,
as well as PUT to modify and GET to view

Spoke v1 implements a driver architecture,
importing pluggable drivers from the Server/v1/Spoke directory
All spoke drivers should super the SpokeDriver class and implement its methods
"""
from flask import Blueprint, request, make_response
import json

from Hub.v1.Common.auth import requires_auth
from Hub.v1.Common.helpers import int_or_string, bool_or_string, parse_request_value

from Hub.v1.Spoke.Spoke import Spoke, SPOKE_DRIVERS


V1SPOKE = Blueprint('V1SPOKE', __name__)

def _parse_schedule_string(schedule_string):
    """
    Convert schedule string from cron format to dictionary.

    Schedule_string passed via value=schedule_string in PUT request
    Format - "MM:HH:[Days]:Action"
    """
    schedule_list = schedule_string.split(":", 3)
    if not len(schedule_list) == 4:
        return False
    parsed_schedule_entry = {"minute" : schedule_list[0],
                             "hour" : schedule_list[1],
                             "days" : schedule_list[2],
                             "action" : bool_or_string(schedule_list[3])}
    return parsed_schedule_entry


@V1SPOKE.route('/v1/spoke', methods=['POST'])
@requires_auth
def new_spoke():
    """
    Create new spoke from input dictionary -

    {'name': <string>, 'driver': <string>, 'driver_info': <dict>}
    """

    spoke_info = request.get_json(silent=True, cache=True)
    spoke = Spoke(**spoke_info)
    spoke.refresh()

    return _spokes_internal(spoke_id=spoke.id)

@V1SPOKE.route('/v1/spokedrivers', methods=['GET'])
@requires_auth
def get_spoke_drivers():
    """Return list of spoke drivers."""
    return json.dumps(SPOKE_DRIVERS)

@V1SPOKE.route('/v1/spoke', methods=['GET'])
@requires_auth
def get_spokes():
    """Get all spokes."""
    return _spokes_internal(**request.args.to_dict(flat=True))

@V1SPOKE.route('/v1/spoke/<path:path>', methods=['GET', 'PUT'])
@requires_auth
def get_spokepath(path):
    """Parse nested spoke path along with optional value parameter for PUTs."""
    parsed_path = path.split("/")
    path = map(int_or_string,
               parsed_path)

    value = parse_request_value(request)

    if len(path) > 1:
        return _spokes_internal(spoke_id=path[0],
                                path=path[1:],
                                value=value)
    elif len(path) == 1:
        return _spokes_internal(spoke_id=path[0],
                                value=value)
    else:
        return _spokes_internal()

@V1SPOKE.route('/v1/spoke/<path:path>', methods=['DELETE'])
@requires_auth
def delete_spoke(path):
    """Handle spoke-related deletion."""
    parsed_path = path.split("/")
    parsed_path = map(int_or_string,
                      parsed_path)

    spoke_id = parsed_path[0]
    if len(parsed_path) == 1: #delete a spoke
        spoke = Spoke.get_id(spoke_id)
        if spoke:
            spoke.delete()
            return ""

    return make_response(json.dumps({"reason" : "InvalidPath"}),
                         404)

def _spokes_internal(spoke_id=None, path=None, value=None, **kwargs):
    """
    Process GET/PUT requests for spoke

    Level indicates level past /spoke/ in the URI
    Return list of spokes if no spoke_id given
    If GET, return specific field asked for by spoke_id & path
    If SET, try to set object described by path to value
    Only specific sets are allowed, enforced either here or at the driver
    InvalidInput strings are a trick to help see where we fell.
    """

    if not spoke_id:
        if value != None:
            return make_response(json.dumps({"reason" : "NotImplemented"}),
                                 501)
        spoke_list = Spoke.list(dict_format=True, **kwargs)
        return json.dumps(spoke_list)
    else:
        spoke = Spoke.get_id(spoke_id)
        if not spoke:
            return make_response(json.dumps({"reason" : "InvalidSpokeID"}),
                                 404)

        spoke_dict = spoke.dict()

        return_value = spoke_dict

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
                #Setting a pin's value - e.g.
                #/spoke/<spoke_id>/pins/<pin_id>/<key> = value
                if path[0] == "pins" and path[1] in list(spoke.pins):
                    if path[2] in ["name", "allocated"]:
                        spoke.pins[path[1]][path[2]] = value
                        spoke.save()
                        return json.dumps(spoke.pins[path[1]][path[2]])
                    elif path[2] == "schedule":
                        #Here we append to the list rather than replace it
                        schedule_dict = _parse_schedule_string(
                            schedule_string=value)
                        spoke.pins[path[1]][path[2]].append(schedule_dict)
                        spoke.save()
                        spoke.update_pin_schedule(spoke.pins[path[1]])
                        return json.dumps(schedule_dict)
                    elif (spoke.driver_class.set_pin(spoke,
                                         spoke.pins[path[1]]['num'],
                                         path[2],
                                         value)):
                        #Let the driver decide if it can handle it
                        spoke.refresh()
                        return json.dumps(spoke.dict())
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
                #/spoke/<spoke_id>/driver_info/<key> = value
                if path[0] == "driver_info":
                    spoke.driver_info[path[1]] = value
                else:
                    return make_response(json.dumps(
                        {"reason" : "NotImplementedPut2"}),
                        501)
                spoke.save()
                spoke_dict = spoke.dict()
                return json.dumps(spoke_dict[path[0]][path[1]])
            elif path_len == 1:
                #Changing a spoke top-level setting - e.g.
                #/spoke/<spoke_id>/<key> = value
                if path[0] == "name":
                    spoke.name = value
                elif path[0] == "driver":
                    spoke.driver = value
                else:
                    return make_response(json.dumps(
                        {"reason" : "NotImplementedPut1"}),
                        501)
                spoke.save()
                spoke_dict = spoke.dict()
                return json.dumps(spoke_dict[path[0]])
            else:
                return make_response(json.dumps(
                    {"reason" : "NotImplementedPut0"}),
                    501)

    return make_response(json.dumps({"reason" : "InvalidInputBottom"}),
                         404)

@V1SPOKE.route('/v1/pin', methods=['GET'])
@requires_auth
def get_pins():
    """Get all 'allocated' pins."""
    return _pins_internal(**request.args.to_dict(flat=True))

@V1SPOKE.route('/v1/pin/<path:path>', methods=['DELETE'])
@requires_auth
def delete_pin(path):
    """Handle pin-related deletion."""
    parsed_path = path.split("/")
    parsed_path = map(int_or_string,
                      parsed_path)

    if len(parsed_path) == 3 and parsed_path[1] == "schedule":
        #delete a schedule entry
        spoke_list = Spoke.list()
        for spoke in spoke_list:
            spoke.refresh()
            if spoke.active and parsed_path[0] in list(spoke.pins):
                try:
                    del spoke.pins[parsed_path[0]][parsed_path[1]][parsed_path[2]]
                    spoke.save()
                    spoke.update_pin_schedule(spoke.pins[parsed_path[0]])
                    return ""
                except (KeyError, IndexError):
                    return make_response(
                        json.dumps({"reason" : "InvalidPath"}),
                        404)

    return make_response(json.dumps({"reason" : "InvalidPath"}),
                         404)

@V1SPOKE.route('/v1/pin/<path:path>', methods=['GET', 'PUT'])
@requires_auth
def get_pinpath(path):
    """Parse nested pin path along with optional value parameter for PUTs."""
    parsed_path = path.split("/")
    path = map(int_or_string,
               parsed_path)

    value = parse_request_value(request)

    if len(path) > 1:
        return _pins_internal(pin_id=path[0],
                              path=path[1:],
                              value=value)
    elif len(path) == 1:
        return _pins_internal(pin_id=path[0],
                              value=value)
    else:
        return _pins_internal()

def _pins_internal(pin_id=None, path=None, value=None, **kwargs):
    """
    Process GET/PUT requests for pin.

    Path is a list indicating levels past /pin/ in the URI
    Only retrieves pins marked 'allocated' unless specific pin_id is given
    If pin_id, request processed same as /spoke/<spoke_id>/pins/<pin_id>
    """

    if not pin_id:
        #Return list of all allocated pins
        if value != None:
            return make_response(json.dumps({"reason" : "InvalidInput"}),
                                 501)
        pin_list = Spoke.list_available_pins(**kwargs)
        return json.dumps(pin_list)
    else:
        #Grab only the object requested
        #Find the spoke that has this pin and pass it off to the spoke handler

        if path == None:
            path = []

        spoke = Spoke.get_for_pin_id(pin_id)
        return _spokes_internal(spoke_id=spoke.id,
                                path=["pins", pin_id] + path,
                                value=value)

    return make_response(json.dumps({"reason" : "PinNotFound"}),
                         404)

