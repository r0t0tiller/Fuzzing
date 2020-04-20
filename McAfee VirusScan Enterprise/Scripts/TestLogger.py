import os

def GetDir():
    try:
        rootDir = "C:\\Fuzzing\\TestDir\\"
        count = 0
        for x in os.listdir(rootDir):
            count +=1
        currentDir = count
    except:
        currentDir = 0
    createDir = int(int(currentDir))
    return createDir

def CreateDir():
    try:
        rootDir = "C:\\Fuzzing\\TestDir\\"
        count = 0
        for x in os.listdir(rootDir):
            count +=1
        currentDir = count
    except:
        currentDir = 0
    createDir = int(int(currentDir) +1)    
    if not os.path.exists(str(rootDir)+str(createDir)):
        os.makedirs(str(rootDir)+str(createDir))
        
def Log():
    POCPath = "C:\\Fuzzing\\TestDir\\"+str(GetDir())+"\\POC.xml"
    POC = "TEST"
    if os.path.isfile(POCPath): # Make sure we don't overwrite POCs
        print "[!] POC already added!"
    else:
        crashPOC = open("C:\\Fuzzing\\TestDir\\"+str(GetDir())+"\\POC.xml",'w')
        crashPOC.write(POC)
        print "[*] POC Logged!"
        
Log()
