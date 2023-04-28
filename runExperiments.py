#!/usr/bin/python                                                                            
                                   
from subprocess import call

if __name__ == '__main__':
	
	protocols = ["bracha","witness","scalable"]
	numberExp = 3
	targetThr = [2**(4+i) for i in range(6)]
	
	for i in range(numberExp):
		for protocol in protocols:
			for th in targetThr:
				inputFile = "ConfigFiles/Experiments/" + protocol + "Input" + str(i) + ".json"
				configFile = "ConfigFiles/Experiments/config" + str(i) + "_" + str(th) + ".json"
				call(["python3", "launch.py", inputFile, configFile])
