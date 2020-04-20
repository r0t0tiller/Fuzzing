import autoit
import os
import time
import glob
import pykd
import sys
import psutil
import os
import random
import os
import shutil
from multiprocessing import Process,Pipe,Queue
from subprocess import Popen, PIPE

EXCEPTION_CODE_AV = 0xc0000005
EXCEPTION_CODE_BREAK = 0x80000003
EXCEPTION_CODE_EH = 0xE06D7363
UNKNOWN_CODE = 0x000006BA

class ExceptionHandler(pykd.eventHandler):

	def __init__(self):
		pykd.eventHandler.__init__(self)
		self.keep_running = True

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

	def KillProcess(self):
		os.system("C:\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe C:\\Fuzzing\\ScanEngine\\KillProcess.ps1")

	def CrashInfo(self):
		# Get register info
		self.registers = pykd.dbgCommand("r")
		self.stack_trace = pykd.dbgCommand("kvb")

	def WriteCrash(self):
		# Write and Print Crash Data
		self.CreateDir()
		self.LoadExploitable()
		self.CrashInfo()
		print ""
		print self.registers
		print self.stack_trace
		print self.exploitable
		print "[*] Logging Crash!"
		crashLog = open("Crashes\\"+str(self.GetDir())+"\\crashlog.txt",'w')
		crashLog.write(self.registers)
		crashLog.write(self.stack_trace)
		crashLog.write(self.exploitable)
		print "[*] Crash Logged!"

	def LogPOC(self):
		print "[*] Logging POC!"
		POC = os.path.join("Queue", os.listdir("Queue")[0])
		POCPath = str(POC)
		DstPath = "Crashes\\"+str(self.GetDir())
		if os.path.isfile(str(DstPath)+"\\"+str(POC)): # Make sure we don't overwrite POCs
			print "[!] POC already added!"
			self.KillProcess()
		else:
			shutil.move(POCPath, DstPath)
			print "[*] POC Logged!"
			self.KillProcess()
				   
	def onException(self, exceptInfo):
		# Only Logging Crashes that cause an Access Violation
		if exceptInfo.exceptionCode == EXCEPTION_CODE_BREAK:
			return pykd.eventResult.Proceed
		elif exceptInfo.exceptionCode == EXCEPTION_CODE_AV:
			self.WriteCrash()
			self.LogPOC()
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
			print ""
			print self.registers
			self.LogPOC()
			return pykd.eventResult.Proceed

class TestcaseGenerator(object):

	def __init__(self):
		self.radamsa_bin = "Generators\\radamsa.exe"
		self.output_dir = "Queue"
		self.maxIterations = 10
		self.testcase_dir = "Testcases"

	def GetTestcase(self):
		testcase = self.testcase_dir + "\\" + random.choice(os.listdir(self.testcase_dir))
		return testcase

	def GetFileExtension(self,path):
		file_extension = os.path.splitext(path)
		return file_extension[1]

	def Generate(self):
		print "[*] Generating...\n",
		createTestcase = self.GetTestcase()
		createFileExtension = self.GetFileExtension(createTestcase)
		p = Popen([self.radamsa_bin,"-o",self.output_dir + "\\%n"+("%s"%createFileExtension), "-n", ("%d"%self.maxIterations), createTestcase])
		p.wait()
		print "[*] Done!"

	def ClearQueue(self):
		print "[*] Clearing Queue..."
		folder = "Queue"
		for the_file in os.listdir(folder):
			file_path = os.path.join(folder, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
			except Exception as e:
				print e

	def CheckDir(self):
		if len(os.listdir("Queue")) == 0:
			print "[!] Queue empty!"
			self.Generate() 

class MonitoringAgent(object):

	def __init__(self):
		self = self

	def GetProcess(self):
		process = filter(lambda p: p.name() == "Scan64.Exe", psutil.process_iter())
		for process_id in process:
			print "[*] PID: %s" % process_id.pid
		return process_id.pid

	def Monitor(self):
		Generator = TestcaseGenerator()
		Generator.CheckDir()
		pykd.initialize()
		Handler = ExceptionHandler()
		testcase = os.listdir("Queue")[0]
		try:
			print "[*] Starting Scan64.exe"
			pykd.startProcess("C:\\Program Files (x86)\\McAfee\\VirusScan Enterprise\\x64\\Scan64.Exe " + testcase)
			pykd.dbgCommand(".childdbg 1")
		except:
			print "[!] Error starting process"
			sys.exit(1)
		try:
			while Handler.keep_running:
				self.GetProcess() # Get PID
				print "[*] Attaching Debugger"
				print "[*] Success!"
				pykd.go()
			print "[*] Killing pykd..."
			pykd.killAllProcesses()
		finally:
			return

	def CheckWindow(self):
		while True:
			try:
				message = autoit.control_get_text("[CLASS:#32770]", "[CLASS:msctls_statusbar32; INSTANCE:1]")
				if message == "Nothing found":
					autoit.win_close("On-Demand Scan Progress")
					self.CheckProcess(False)
			except autoit.autoit.AutoItError:
				pass

	def CheckProcess(self, flag):
		processFlag = flag
		if processFlag == False:
			topTestcase = os.path.join("Queue", os.listdir("Queue")[0])
			os.unlink(topTestcase)
			print "[!] Restarting!"
			os.system("C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe C:\\Fuzzing\\ScanEngine\\KillProcess.ps1")

def MonitorWorker(q):
	monitorObj = q.get()
	monitorObj.Monitor()

def WindowWorker(q):
	windowObj = q.get()
	windowObj.CheckWindow()

def Start():
	monitorQueue = Queue()
	windowQueue = Queue()

	p1 = Process(target=MonitorWorker, args=(monitorQueue,))
	p1.start()

	p2 = Process(target=WindowWorker, args=(windowQueue,))
	p2.start()

	monitorQueue.put(MonitoringAgent())
	windowQueue.put(MonitoringAgent())

	monitorQueue.close()
	monitorQueue.join_thread()
		
	windowQueue.close()
	windowQueue.join_thread()

if __name__=='__main__':
	Start()