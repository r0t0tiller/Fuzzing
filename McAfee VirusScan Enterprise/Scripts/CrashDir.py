import os

def GetDir():
    try:
        rootDir = "C:\\Fuzzing\\Crashes\\"
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
        rootDir = "C:\\Fuzzing\\Crashes\\"
        count = 0
        for x in os.listdir(rootDir):
            count +=1
        currentDir = count
    except:
        currentDir = 0
    createDir = int(int(currentDir) +1)    
    if not os.path.exists(str(rootDir)+str(createDir)):
        os.makedirs(str(rootDir)+str(createDir))
