#!/usr/bin/python                                                                            
                                   
from subprocess import call

if __name__ == '__main__':
	
	protocols = ["bracha","witness","scalable"]
	#targetThr = [2*(i+1) for i in range(64)] #
	targetN = [4, 8, 16]
	#numberExp = 8
	dictFiles = {4:"0", 8:"1", 16:"2"}
	
	"""
	for nNodes in targetN:
		for i in range(3):
			for protocol in protocols:
				inputFile = "ConfigFiles/Experiments/" + protocol + "Input" + dictFiles[nNodes] + ".json"
				configFile = "ConfigFiles/Experiments/stress" + str(i) + ".json"
				call(["python3", "launchMesh.py", inputFile, configFile])
				
	
	for nNodes in targetN:
		step = (128//nNodes)*4
		for _ in range(numberExp):
			for protocol in protocols:
				inputFile = "ConfigFiles/Experiments/" + protocol + "Input" + dictFiles[nNodes] + ".json"
				configFile = "ConfigFiles/Experiments/config" + dictFiles[nNodes] + "_" + str(step) + ".json"
				call(["python3", "launchMesh.py", inputFile, configFile])
			step += step
				
	"""
	
	for nNodes in targetN:
		for protocol in protocols:
			inputFile = "ConfigFiles/Experiments/" + protocol + "Input" + dictFiles[nNodes] + ".json"
			configFile = "ConfigFiles/Experiments/config" + dictFiles[nNodes] + "_" + "16" + ".json"
			call(["python3", "launchMesh.py", inputFile, configFile])
