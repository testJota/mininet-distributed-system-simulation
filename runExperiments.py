#!/usr/bin/python                                                                            
                                   
from subprocess import call
import math

if __name__ == '__main__':
	
	protocols = ["bracha","witness","scalable"]
	#protocols = ["bracha","scalable"]
	numberInputs = 9
	numberExp = 9
	
	targetThr = [math.ceil(2**((i+6)/3)) for i in range(22)]
	
	for th in targetThr:
		for i in range(1,numberInputs):
			for protocol in protocols:
				#for j in range(numberExp):
					# Latency test
					#inputFile = "ConfigFiles/Experiments/" + protocol + "Input" + str(i) + ".json"
					#configFile = "ConfigFiles/Experiments/best" + str(j) + ".json"
					#call(["python3", "launchMesh.py", inputFile, configFile])
					
					# Throughput test
					#inputFile = "ConfigFiles/Experiments/" + protocol + "Input" + str(i) + ".json"
					#configFile = "ConfigFiles/Experiments/stress" + str(j) + ".json"
					#call(["python3", "launchMesh.py", inputFile, configFile])
					
					# Main test
				inputFile = "ConfigFiles/Experiments/" + protocol + "Input" + str(i) + ".json"
				configFile = "ConfigFiles/Experiments/config16_" + str(th) + ".json"
				call(["python3", "launch.py", inputFile, configFile])
