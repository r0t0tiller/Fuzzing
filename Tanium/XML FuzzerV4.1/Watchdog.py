import psutil
import os
from time import sleep

def GetStats():
        print "[*] CPU Usage: %s" % str(psutil.cpu_percent()) + "%"
        print "[*] Memory Usage: %s" % str(psutil.virtual_memory()[2]) + "%"

def Watch():
    print "[*] Watchdog Started!"
    while True:
        sleep(300)
        PROCNAME = "python.exe"
        count = 0
        for proc in psutil.process_iter():
            if proc.name() == PROCNAME:
                count = count + 1
        if count == 2:
            print "[!] Fuzzer is down!"
            print "[!] Restarting the fuzzer!"
            os.system("powershell.exe Start-Process powershell.exe -ArgumentList 'C:\\Fuzzing\\RestartFuzzer.ps1'")
        elif count == 1:
            print "[!] Both Monitor and Fuzzer is down!"
        else:
            print "[*] All systems go!"
            GetStats()
Watch()
