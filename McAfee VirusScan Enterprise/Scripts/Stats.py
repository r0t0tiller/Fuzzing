import psutil
from time import sleep

def GetStats():
    while True:
        sleep(1)
        print "CPU Usage: %s" % str(psutil.cpu_percent()) + "%"
        print "Memory Usage: %s" % str(psutil.virtual_memory()[2]) + "%"

GetStats()

    
