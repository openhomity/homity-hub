"""Random helper functions."""
from commands import getstatusoutput

def int_or_string(string):
    """Return an int if possible, else string."""
    try:
        return int(string)
    except ValueError:
        return str(string)

def bool_or_string(string):
    """Return bool if possible, else string."""
    if string == True or str(string).strip().lower() in ('t', 'true', 'yes', '1'):
        return True
    elif string == False or str(string).strip().lower() in ('f', 'false', 'no', '0'):
        return False
    else:
        return str(string)

def update_crontab(object_name="", new_schedule=None):
    """
    Update crontab with object's schedule.

    Linux crontab used for scheduling
    Each entry in the crontab is labeled with the object_name
    of the requestor so it can be blown away later
    Expects new_schedule as list of dicts
    [{"minute" : <minute>, "hour" : <hour>,
    "days" : <days>, "command" : <linux_command_string>}]
    If called without an object name it will blow away
    the whole table and replace it with new_schedule
    If called without a new_schedule it will delete all instances of an object
    """

    if new_schedule == None:
        new_schedule = []

    cmd = "crontab -l | grep -v \"%s\"" % (object_name)
    status, cleaned_file = getstatusoutput(cmd)
    temp_crontab = open("/tmp/crontab.txt", "w")

    try:
        if cleaned_file.split()[1] != "crontab":
            temp_crontab.write(str(cleaned_file))
    except IndexError:
        pass

    temp_crontab.write("\n")

    for entry in new_schedule:
        temp_crontab.write("%s   %s  *   *   %s  %s   #%s \n" %
                           (entry['minute'],
                            entry['hour'],
                            entry['days'],
                            entry['command'],
                            object_name))

    temp_crontab.close()
    getstatusoutput("crontab /tmp/crontab.txt")

