from commands import getstatusoutput

def int_or_string (s):
    try:
        return int(s)
    except ValueError:
        return str(s)
    
def bool_or_string(string):
    if string in ['True', 'true', 'TRUE']:
        return True
    if string in ['False', 'false', 'FALSE']:
        return False
    else:
        return str(string)

#Linux crontab used for scheduling
#Each entry in the crontab is labeled with the object_name of the requestor so it can be blown away later
#Expects new_schedule as list of dicts [{"minute" : <minute>, "hour" : <hour>, "days" : <days>, "command" : <linux_command_string>}]
#If called without an object name it will blow away the whole table and replace it with new_schedule
#If called without a new_schedule it will delete all instances of an object
def update_crontab(object_name="", new_schedule=[]):
    #clear existing crontab entries for this object
    cmd = "crontab -l | grep -v \"%s\"" % (object_name)
    status,cleaned_file = getstatusoutput(cmd)
    temp_crontab = open("/tmp/crontab.txt","w")
    if cleaned_file.split()[1] != "crontab":  # avoid "no crontab for x" issues
        temp_crontab.write(str(cleaned_file))
    
    #walk new_schedule and insert entries into temp crontab file
    temp_crontab.write("\n")
    for entry in new_schedule:
        temp_crontab.write("%s   %s  *   *   %s  %s   #%s \n" % (entry['minute'], entry['hour'], entry['days'], entry['command'],object_name))
    
    temp_crontab.close()
    getstatusoutput("crontab /tmp/crontab.txt")
