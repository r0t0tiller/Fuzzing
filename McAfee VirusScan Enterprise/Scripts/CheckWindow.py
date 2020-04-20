import autoit
import os
import time

def CheckWindow():
	#autoit.run("C:\\Program Files (x86)\\McAfee\\VirusScan Enterprise\\x64\\Scan64.Exe")
	#autoit.win_wait_active("On-Demand Scan Progress",3)
	while True:
		try:
			message = autoit.control_get_text("[CLASS:#32770]", "[CLASS:msctls_statusbar32; INSTANCE:1]")
			if message == "Nothing found":
				autoit.win_close("On-Demand Scan Progress")
		except autoit.autoit.AutoItError:
			os.system("powershell.exe Start-Process powershell.exe -ArgumentList C:\\Fuzzing\\ScanEngine\\Restart.ps1")
			CheckWindow()
def Main():
	CheckWindow()

Main()
