import sys
import psutil
import pykd
import requests
import os
from time import sleep

EXCEPTION_CODE_AV = 0xc0000005
EXCEPTION_CODE_BREAK = 0x80000003
EXCEPTION_CODE_EH = 0xE06D7363

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

    def GetDir(self):
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
        crashLog = open("C:\\Fuzzing\\Crashes\\"+str(self.GetDir())+"\\crashlog.txt",'w')
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
        else:
            print "[!] Unknown Exception!"
            self.CreateDir()
            self.registers = pykd.dbgCommand("r")
            crashLog = open("C:\\Fuzzing\\Crashes\\"+str(self.GetDir())+"\\unknown_crashlog.txt",'w')
            crashLog.write(self.registers)
            print self.registers
            return pykd.eventResult.Proceed       

def CheckStatus():
    print "[*] Checking Tanium Server Status"
    isOnline = False
    while isOnline == False:
        checker = """<?xml version="1.0" encoding="utf-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SOAP-ENV:Body>
    <typens:tanium_soap_request xmlns:typens="urn:TaniumSOAP">
      <command>GetObject</command>
      <object_list>
        <groups>
          <group>
            <name>Check</name>
          </group>
        </groups>
      </object_list>
    </typens:tanium_soap_request>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""
        try:
            requests.packages.urllib3.disable_warnings()
            URL = "https://localhost/soap/"
            headers = {'Host':'127.0.0.1', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate','DNT':'1', 'Accept-Language': 'en-US,en;q=0.5'}
            requests.post(URL, data=checker, headers=headers, verify=False)
            print "[*] Tanium Server is ONLINE"
            isOnline = True
        except:
             print "[*] Tanium Server is OFFLINE"
        sleep(1)

def Monitor():
    print "[*] Attaching to TaniumReceiver.exe"
    process = filter(lambda p: p.name() == "TaniumReceiver.exe", psutil.process_iter())
    for process_id in process:
      print "[*] PID: %s" % process_id.pid
    pykd.initialize()
    Handler = ExceptionHandler()
    try:
        pykd.attachProcess(process_id.pid)
    except:
        print "[!] Error attaching to process"
        sys.exit(1)
    print "[*] Success!"
    pykd.go()

def StartFuzzer():
    print "[*] Starting Fuzzer!"
    os.system("powershell.exe Start-Process powershell.exe -ArgumentList 'C:\\Fuzzing\\RunFuzzer.ps1'") # Fuzzer
    os.system("powershell.exe Start-Process powershell.exe -ArgumentList 'C:\\Fuzzing\\RunWatchdog.ps1'") # Watchdog
    

def Main():
    CheckStatus()
    StartFuzzer()
    Monitor()

Main()
