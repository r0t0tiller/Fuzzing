import os
import sys
from time import sleep

def GetDir():
    try:
        rootDir = "C:\\Fuzzing\\Crashes\\"
        for x in os.listdir(rootDir):
            currentDir = x
        currentDir = max(currentDir)
    except:
        currentDir = 0
    createDir = int(int(currentDir))
    return createDir

def LogPOC():
    print "[*] Logging POC!"
    POC = "TEST"
    sleep(3) # Time to allow Monitor.py to create the folder
    filePath = "C:\\Fuzzing\\Crashes\\"+str(GetDir())+"\\POC.xml"
    if os.path.isfile(filePath): # Make sure we don't overwrite POCs
        print "[!] POC already added!" 
        sys.exit(1)
    else:
        crashPOC = open("C:\\Fuzzing\\Crashes\\"+str(GetDir())+"\\POC.xml",'w')
        crashPOC.write(POC)
        print "[*] POC Logged!"
LogPOC()
