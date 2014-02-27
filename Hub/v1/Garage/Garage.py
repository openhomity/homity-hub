"""Garage controller object."""
from couchdb.mapping import Document, TextField, BooleanField, DictField
from uuid import uuid4
from sys import modules

from Hub.v1.Garage.Garage_Driver import GarageDriver
from Hub.v1.Common.base import HomityObject

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

class GarageController(HomityObject):
    """
    Garage controller object.

        {
            "garage_id" : {
                "id" : <uuid of garage>
                "name" : <name of garage>
                "allocated" : <True if garage is being used>
                "num" : <GarageController identifier for garage>
                "open" : <True if garage is open>
                "on" : <True if garage is turned on>
                "location" : <name of parent garage controller>
                "controller" : <id of parent garage controller>
            }
        }
    """
    name = TextField()
    active = BooleanField()
    driver = TextField()
    driver_info = DictField()

    garages = DictField()

    def status(self):
        """Return dict of garage controller status."""
        if self.active:
            status_dict = {"name" : self.name,
                           "driver" : self.driver,
                           "driver_info" : self.driver_info,
                           "id" : self.id,
                           "garages" : self.garages,
                           "active" : self.active}
        else:
            status_dict = {"name" : self.name,
                           "driver" : self.driver,
                           "driver_info" : self.driver_info,
                           "id" : self.id,
                           "active" : self.active}
        return status_dict

    def _add_garage(self, garage_num, garage):
        """Populate fields for new garage object."""
        garage_id = uuid4().hex
        self.garages[garage_id] = {'allocated' : False,
                                   'num' : garage_num,
                                   'id' : garage_id,
                                   'name' : "",
                                   'open' : garage.get('open'),
                                   'on' : garage.get('on'),
                                   'controller' : self.id,
                                   'location' : self.name}

    def update_garages(self, garage_status=None):
        """Update status for garages belonging to controller."""
        if garage_status == None:
            garage_status = {}

        if self.active:
            existing_garage_nums_to_ids = ({item.get('num'):item.get('id') for
                                            item in self.garages.values()})
            for garage_num, garage in garage_status.items():
                if garage_num in list(existing_garage_nums_to_ids):
                    garage_id = existing_garage_nums_to_ids.get(garage_num)
                    self.garages[garage_id]['open'] = garage.get('open')
                    self.garages[garage_id]['on'] = garage.get('on')
                else:
                    self._add_garage(garage_num, garage)
        return True
