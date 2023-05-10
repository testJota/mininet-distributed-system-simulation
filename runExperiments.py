#!/usr/bin/python                                                                            
                                   
from subprocess import call

if __name__ == '__main__':
	
	protocols = ["bracha","witness","scalable"]
	numberInputs = 5
	numberExp = 5
	
	for i in range(numberInputs):
		for protocol in protocols:
			for j in range(numberExp):
				# Latency test
				inputFile = "ConfigFiles/Experiments/" + protocol + "Input" + str(i) + ".json"
				configFile = "ConfigFiles/Experiments/best" + str(j) + ".json"
				call(["python3", "launchMesh.py", inputFile, configFile])
				
				# Throughput test
				inputFile = "ConfigFiles/Experiments/" + protocol + "Input" + str(i) + ".json"
				configFile = "ConfigFiles/Experiments/stress" + str(j) + ".json"
				call(["python3", "launchMesh.py", inputFile, configFile])
