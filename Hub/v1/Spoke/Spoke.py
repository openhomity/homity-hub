"""Spoke controller object."""
from couchdb.mapping import Document, TextField, BooleanField, DictField
from uuid import uuid4

from Hub.v1.Common.helpers import update_crontab


class Spoke(Document):
    """
    Spoke controller object.
        {
        "pin_id" : {
            "id" : <uuid of pin>
            "name" : <name of pin>
            "allocated" : <True if pin is being used>
            "digital" : <True if pin status bool, False if int>
            "output" : <True if pin status is settable, False if readable>
            "num" : <Spoke's identifier for pin>
            "value" : <True|False if digital, integer if analog>
            "schedule" : [
                "action" : <True turning on>
                "minute" : <minute to perform action>
                "hour" : <hour to perform action>
                "days" : <[0,1,2], or [0-6], Sunday=0>
            ]
        }
        }"""
    name = TextField()
    active = BooleanField()
    driver = TextField()
    driver_info = DictField()
    pins = DictField()

    def status(self):
        """
        Return status of spoke.

        Todo - investigate replacing with __repr__
        """
        #self.refresh_status()
        driver_ext = {}
        #driver_ext = driver.get_ext_info()
        if self.active:
            status_dict = {"name" : self.name,
                           "driver" : self.driver,
                           "driver_info" : self.driver_info,
                           "id" : self.id,
                           "pins" : self.pins,
                           "active" : self.active,
                           "driver_ext" : driver_ext}
        else:
            status_dict = {"name" : self.name,
                           "driver" : self.driver,
                           "driver_info" : self.driver_info,
                           "id" : self.id,
                           "pins" : {},
                            "active" : self.active,
                            "driver_ext" : driver_ext}
        return status_dict

    def _add_pin(self, pin_num, pin):
        """Add new pin to object."""
        pin_id = uuid4().hex
        self.pins[pin_id] = {
            'allocated' : False,
            'num' : pin_num,
            'id' : pin_id,
            'name' : "",
            'schedule' : [],
            'digital' : pin.get('digital'),
            'output' : pin.get('output'),
            'spoke' : self.id,
            'location' : self.name
            }
        if pin.get('digital'):
            self.pins[pin_id]['status'] = pin.get('on')
        else:
            self.pins[pin_id]['status'] = pin.get('value')

    def update_pins(self, pin_status=None):
        """Update object according to what we get from driver."""

        if pin_status == None:
            pin_status = {}
        if self.active:
            existing_pin_nums_to_ids = ({item.get('num'):item.get('id') for
                                         item in self.pins.values()})
            for pin_num, pin in pin_status.items():
                if pin_num in list(existing_pin_nums_to_ids):
                    pin_id = existing_pin_nums_to_ids.get(pin_num)
                    self.pins[pin_id]['digital'] = pin.get('digital')
                    self.pins[pin_id]['output'] = pin.get('output')
                    self.pins[pin_id]['location'] = self.name
                    if pin.get('digital'):
                        self.pins[pin_id]['status'] = pin.get('on')
                    else:
                        self.pins[pin_id]['status'] = pin.get('value')
                else:
                    self._add_pin(pin_num,
                                  pin)
        return True

    def update_pin_schedule(self, pin, driver_shell_commands):
        """
        Update cron for pin schedule.

        Used only for digital output pins to turn on/off
        Driver_actions is a dict containing -
        {"True": <linux cmd to turn on>, "False": <linux cmd to turn off>}
        """
        def action_to_command(x):
            """Convert true/false action to shell cmd."""
            x['command'] = driver_shell_commands[str(x['action'])]
            return x
        map(action_to_command,
            pin['schedule'])
        if pin['digital'] and pin['output']:
            update_crontab("%s %s" % (pin['id'], self.id), pin['schedule'])

    def clear_spoke_schedule(self):
        """Clear all pin schedule entries."""
        update_crontab(self.id)
