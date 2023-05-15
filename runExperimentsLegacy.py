#!/usr/bin/python                                                                            
                                   
from subprocess import call

if __name__ == '__main__':
	
	protocols = ["bracha","witness","scalable"]
	#targetThr = [2*(i+1) for i in range(64)] #
	targetN = [100]
	numberExp = 8
	dictFiles = {100:"5"}
				
	
	for nNodes in targetN:
		step = 4
		current = 4
		for _ in range(numberExp):
			for protocol in protocols:
				inputFile = "ConfigFiles/Experiments_Legacy/" + protocol + "Input" + dictFiles[nNodes] + ".json"
				configFile = "ConfigFiles/Experiments_Legacy/config" + dictFiles[nNodes] + "_" + str(current) + ".json"
				call(["python3", "launchMesh.py", inputFile, configFile])
			current += step
