#!/usr/bin/python                                                                            
                                   
from subprocess import call

if __name__ == '__main__':
	
	#protocols = ["bracha","witness","scalable"]
	protocols = ["bracha"]
	initialExp = 2
	finalExp = 3 # The last experiment is finalExp - 1
	targetThr = [int((2**(1/2))**(4+i)) for i in range(10)]
	
	for th in targetThr:
		for protocol in protocols:
			for i in range(initialExp, finalExp):	
				inputFile = "ConfigFiles/Experiments/" + protocol + "Input" + str(i) + ".json"
				configFile = "ConfigFiles/Experiments/config" + str(i) + "_" + str(th) + ".json"
				call(["python3", "launch.py", inputFile, configFile])
