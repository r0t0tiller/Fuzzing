import requests
from subprocess import Popen, PIPE
import sys
from time import sleep
import glob
import signal
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
        sleep(5) # Delay to ensure the Monitor has started

def KillAll():
    os.system("powershell.exe Start-Process powershell.exe -ArgumentList 'C:\\Fuzzing\\KillAll.ps1'") # KillAll

def Fuzz():
        radamsa_bin = "C:\\Fuzzing\\Generators\\radamsa.exe"
        while True:
            for filename in glob.iglob('Testcases/*.xml'):
                print "[*] Testcase: %s\n" % (filename)
                with open(filename, "r") as filehandle:
                    filecontent = filehandle.read()
                    ready_contents = filecontent
                    try:
                        try:
                            radamsa = [radamsa_bin]
                            p = Popen(radamsa, stdin=PIPE, stdout=PIPE)
                            mutated_data = p.communicate(ready_contents)[0]
                        except:
                            print "Could not execute 'radamsa'."
                            sys.exit(1)
                        print "[*] Sending...\n"
                        print mutated_data
                        POC = mutated_data
                        headers = {'Host': '127.0.0.1', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate','DNT':'1', 'Accept-Language': 'en-US,en;q=0.5'} # set what your server accepts
                        print "\n[*] Response:\n"
                        try:
                            print requests.post('https://127.0.0.1/soap/', data=mutated_data, headers=headers, verify=False,timeout=300).text 
                        except requests.exceptions.Timeout: # 5 minute timeout
                            print "[!] Hang Detected!"
                            print "[!] Restarting Fuzzer!"
                            sleep(3) # Delay before fuzzer is restarted
                            KillFuzzer()
                    except Exception as err:
                        print "[*] Exception: %s" % str(err)
                        print "[*] Tanium Server is OFFLINE"
                        return LogPOC(POC)

def LogPOC(POC):
    print "[*] Logging POC!"
    sleep(3) # Time to allow Monitor.py to create the folder
    POCPath = "C:\\Fuzzing\\Crashes\\"+str(GetDir())+"\\POC.xml"
    if os.path.isfile(POCPath): # Make sure we don't overwrite POCs
        print "[!] POC already added!"
        KillAll() # Restart everything
        sys.exit(1)
    else:
        crashPOC = open("C:\\Fuzzing\\Crashes\\"+str(GetDir())+"\\POC.xml",'w')
        crashPOC.write(POC)
        print "[*] POC Logged!"
        KillAll() # Restart everything
    
def Main():
        CheckStatus()
        Fuzz()
Main()
