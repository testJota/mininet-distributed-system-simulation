#!/usr/bin/python                                                                            
     
from time import time                   
from time import sleep        
from signal import SIGINT
from subprocess import call
#import threading
import json
import sys
import os
                                                                                             
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
#from mininet.node import CPULimitedHost
from mininet.link import TCULink
from mininet.node import Controller, RemoteController
from mininet.util import pmonitor
from mininet.cli import CLI

from generateTopo import generateMininetTopo

class CustomTopo(Topo):
	"Single switch connected to n hosts."
	def build(self, net_topo, testNodes):
		
		for net in net_topo['networks'].keys():
			self.addSwitch(net)
			if net_topo['networks'][net] != None:
				for net_ in net_topo['networks'][net].keys():
					args = net_topo['networks'][net][net_]
					self.addLink(net, net_,**args)
		
		n = len(net_topo['peers'].keys())
		for peer in net_topo['peers'].keys():
			#self.addHost(peer,cpu=.1/n)
			self.addHost(peer)
			for net_ in net_topo['peers'][peer].keys():
				args = net_topo['peers'][peer][net_]
				self.addLink(peer, net_,**args)
		
		numberHosts = len(net_topo['peers'].keys())
		numberSwitches = len(net_topo['networks'].keys())
		if testNodes["inTestNodes"]:
			testNode1 = "h" + str(numberHosts)
			testNode2 = "h" + str(numberHosts+1)
			testSwitch1 = "s0"
			testSwitch2 = "s" + str(numberSwitches-1)
			self.addHost(testNode1)
			self.addLink(testNode1,testSwitch1,bw=.1,delay=testNodes["inTopoDelay"],loss=0,max_queue_size=100)
			self.addHost(testNode2)
			self.addLink(testNode2,testSwitch2,bw=.1,delay=testNodes["inTopoDelay"],loss=0,max_queue_size=100)
			numberHosts += 2
			
		if testNodes["outTestNodes"]:
			testNode1 = "h" + str(numberHosts)
			testNode2 = "h" + str(numberHosts+1)
			testSwitch = "s" + str(numberSwitches)
			self.addSwitch(testSwitch)
			self.addHost(testNode1)
			self.addLink(testNode1,testSwitch,bw=.1,delay=testNodes["outTopoDelay"],loss=0,max_queue_size=100)
			self.addHost(testNode2)
			self.addLink(testNode2,testSwitch,bw=.1,delay=testNodes["outTopoDelay"],loss=0,max_queue_size=100)

		
def simpleTest(inputPath, configPath):

	call(["mn","-c"])
	
	# Read input file
	with open(inputPath, 'r') as myfile:
		data = myfile.read()
		
	obj = json.loads(data)

	nHosts = obj['parameters']['n']

	with open(configPath, 'r') as confFile:
		sim_conf =  confFile.read()

	# parse file
	sim_conf = json.loads(sim_conf)

	# read topo file
	pathTopoFile = "Topos/" + sim_conf["topology"]

	with open(pathTopoFile, 'r') as topoFile:
		net_topo =  topoFile.read()

	# parse file
	net_topo = json.loads(net_topo)
	
	fullTopo = generateMininetTopo(net_topo, 32, sim_conf["hostBand"], 
				sim_conf["hostQueue"], sim_conf["hostDelay"], sim_conf["hostLoss"])

	"Create and test a simple network"
	topo = CustomTopo(fullTopo, sim_conf["testNodes"])
	net = Mininet(topo, link=TCULink, build=False, waitConnected=False)
	net.addController( RemoteController( 'c0', ip='127.0.0.1', port=6633 ))
	net.build()
	
	try:
		net.start()
		
		switch = 's0'

		for i in range(1,nHosts+1):
			cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst=10.0.0.{i},actions=output:"{switch}-eth{i}"'
			print(cmd)
			os.system(cmd)
			cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst=10.0.0.{i},actions=output:"{switch}-eth{i}"'
			print(cmd)
			os.system(cmd)

		os.system(f"ovs-ofctl dump-flows {switch}")	

		print( "Dumping switch connections" )
		dumpNodeConnections(net.switches)
		
		print( "Setting up main server" )
		hosts = net.hosts
		
		popens = {}

		# server execution code
		cmd = "./mainserver --n " + str(nHosts) + " --log_file outputs/mainOut.txt" + " --topo star" + " --nodes 32"
		popens["Main"] = hosts[0].popen(cmd)
		print(inputPath + ", " + configPath)

		sleep(1) # time to setup main server

		print( "Setting up nodes" )
		
		clientSet = set([x for x in range(16)])

		for i in range(nHosts):
		
			# node execution code
			nodeId = str(i)
			inputFile = "--input_file " + inputPath
			logFile = "--log_file outputs/process" + nodeId + ".txt"
			
			if sim_conf["numberTransactions"] == -1:
				nTr = "--stress_test true"
				trDelay = "--transaction_init_timeout_ns " + str(sim_conf["transactionDelay"])
			elif sim_conf["numberTransactions"] == -2:
				if i == 0:
					nTr = "--stress_test true"
					trDelay = "--transaction_init_timeout_ns " + str(sim_conf["transactionDelay"])
				else:
					nTr = "--transactions " + "0"
					trDelay = "--transaction_init_timeout_ns " + str(sim_conf["transactionDelay"])
			else:
				if clientSet:
					nTr = "--transactions " + str(sim_conf["numberTransactions"])
					trDelay = "--transaction_init_timeout_ns " + str(sim_conf["transactionDelay"])
					clientSet.pop()
				else:
					nTr = "--transactions " + "0"
					trDelay = "--transaction_init_timeout_ns " + str(sim_conf["transactionDelay"])
				
			cmd = "./node " + inputFile + " " + logFile + " --i " + nodeId + " " + nTr + " " + trDelay + " --topo star" + " --nodes 32" + " 2>&1"
			
			#popens[hosts[i+1]] = hosts[i+1].popen(cmd, shell=True)
			popens[str(i)] = hosts[(i) % 32].popen(cmd, shell=True)
			
		#CLI(net)	
		
		info( "Monitoring output for", sim_conf["simulationTime"], "seconds\n" )
		endTime = time() + sim_conf["simulationTime"]
		for h, line in pmonitor( popens, timeoutms=100 ):
			if h:
				info( '<%s>: %s' % ("P" + h, line ) )
			if time() >= endTime:
				print("Sending termination signal...")
				for p in popens.values():
					p.send_signal( SIGINT )
				break

		info("Simulation end... ")
		
		net.stop()
		
	finally:
		call("sudo pkill -f node", shell = True)
		call("sudo pkill -f mainserver", shell = True)
		call(["mn","-c"])
		
		info("Compressing outputs...")
		firstName = inputPath.split("/")[-1]
		lastName = configPath.split("/")[-1]
		fileName = "outputs/compressed/" + firstName.split(".")[0] + lastName.split(".")[0] + ".tar.gz"
		listFiles = ["tar","-czf",fileName,"outputs/mainOut.txt"]
			
		for i in range(nHosts):
			listFiles.append(f"outputs/process{i}.txt")
			
		# Compressing files
		call(listFiles)
		
		info("The end \n")

if __name__ == '__main__':
	"""
		Usage: sudo python3 launch.py inputPath configPath
	"""
	# Tell mininet to print useful information
	setLogLevel('info')
	simpleTest(sys.argv[1], sys.argv[2])
