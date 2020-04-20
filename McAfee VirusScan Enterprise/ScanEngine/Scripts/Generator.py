import glob
import sys
import random
import os
import shutil
from subprocess import Popen, PIPE

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
		p = Popen([self.radamsa_bin,"-o",self.output_dir + "\\%n"+("%s"%createFileExtension), "-n", ("%d"%self.maxIterations), createTestcase,"-M","meta.txt"])
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
		if len(os.listdir('Queue')) == 0:
			print "[*] Queue empty"
			self.Generate() 

def main():

	Generate = TestcaseGenerator()
	Generate.ClearQueue()
	#Generate.Generate()
	Generate.CheckDir()

main()