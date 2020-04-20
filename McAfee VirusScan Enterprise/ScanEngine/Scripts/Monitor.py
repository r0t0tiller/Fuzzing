import pykd
import sys
import psutil
import os

EXCEPTION_CODE_AV = 0xc0000005
EXCEPTION_CODE_BREAK = 0x80000003
EXCEPTION_CODE_EH = 0xE06D7363
UNKNOWN_CODE = 0x000006BA

class ExceptionHandler(pykd.eventHandler):
    def __init__(self):
        pykd.eventHandler.__init__(self)

    def LoadExploitable(self):
        # Load !exploitable
        extHandle = pykd.loadExt("C:\\Fuzzing\\Libs\\MSEC.dll")
        print "[*] MSEC at 0x%x" % extHandle
        commandOutput = pykd.callExt(extHandle,"exploitable", "-v")
        self.exploitable=commandOutput
        
    def CreateDir(self):
        try:
            rootDir = "Crashes\\"
            count = 0
            for x in os.listdir(rootDir):
                count +=1
            currentDir = count
        except:
            currentDir = 0
        createDir = int(int(currentDir) +1)
        if not os.path.exists(str(rootDir)+str(createDir)):
            os.makedirs(str(rootDir)+str(createDir))

    def GetDir(self):
        try:
            rootDir = "Crashes\\"
            count = 0
            for x in os.listdir(rootDir):
                count +=1
            currentDir = count
        except:
            currentDir = 0
        createDir = int(int(currentDir))
        return createDir

    def CrashInfo(self):
        # Get register info
        self.registers = pykd.dbgCommand("r")
        self.stack_trace = pykd.dbgCommand("kvb")

    def WriteCrash(self):
        # Write and Print Crash Data
        self.CreateDir()
        self.LoadExploitable()
        self.CrashInfo()
        print self.registers
        print self.stack_trace
        print self.exploitable
        print "[*] Logging Crash!"
        crashLog = open("Crashes\\"+str(self.GetDir())+"\\crashlog.txt",'w')
        crashLog.write(self.registers)
        crashLog.write(self.stack_trace)
        crashLog.write(self.exploitable)
        print "[*] Crash Logged!"
                   
    def onException(self, exceptInfo):
        # Only Logging Crashes that cause an Access Violation
        if exceptInfo.exceptionCode == EXCEPTION_CODE_BREAK:
            return pykd.eventResult.Proceed
        elif exceptInfo.exceptionCode == EXCEPTION_CODE_AV:
            self.WriteCrash()
        elif exceptInfo.exceptionCode == EXCEPTION_CODE_EH:
            return pykd.eventResult.NoChange
        elif exceptInfo.exceptionCode == UNKNOWN_CODE:
            return pykd.eventResult.NoChange
        else:
            print "[!] Unknown Exception!"
            self.CreateDir()
            self.registers = pykd.dbgCommand("r")
            crashLog = open("Crashes\\"+str(self.GetDir())+"\\unknown_crashlog.txt",'w')
            crashLog.write(self.registers)
            print self.registers
            return pykd.eventResult.Proceed

def GetProcess():
    process = filter(lambda p: p.name() == "Scan64.Exe", psutil.process_iter())
    for process_id in process:
      print "[*] PID: %s" % process_id.pid
      return process_id.pid

def Monitor():
    testcase = "Testcases\\Test.txt"
    try:
        pykd.initialize()
        Handler = ExceptionHandler()
        print "[*] Starting Scan64.exe"
        pykd.startProcess("C:\\Program Files (x86)\\McAfee\\VirusScan Enterprise\\x64\\Scan64.Exe " + testcase)
        pykd.dbgCommand(".childdbg 1")
    except:
        print "[!] Error starting process"
        sys.exit(1)
    print "[*] Success!"
    pykd.go()

Monitor()