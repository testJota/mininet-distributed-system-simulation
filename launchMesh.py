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
from mininet.node import CPULimitedHost, Controller, RemoteController
from mininet.link import TCULink
from mininet.util import pmonitor

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

def meshRules(nHosts, nSwitches):
	hSwitches = round(nHosts**(1/2)+0.5)
	
	sRanges = []
	for i in range(nSwitches):
		sRange = [k for k in range(hSwitches*i+1,hSwitches*(i+1)+1)]
		sRanges.append(sRange)
		
	for i in range(nSwitches):
		switch = "s" + str(i)
		orderDict = orderSwitches(i, nSwitches)
		offset0 = 0
		if i == (nSwitches-1):
			cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=60,priority=100,dl_type=0x0800,nw_dst=10.0.0.{1},actions=output:"{switch}-eth{hSwitches}"'
			print(cmd)
			os.system(cmd)
			cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=60,priority=100,dl_type=0x0806,nw_dst=10.0.0.{1},actions=output:"{switch}-eth{hSwitches}"'
			print(cmd)
			os.system(cmd)
			offset0 = 1
		else:
			cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=60,priority=100,dl_type=0x0800,nw_dst=10.0.0.{1},actions=output:"{switch}-eth{nSwitches-1}"'
			print(cmd)
			os.system(cmd)
			cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=60,priority=100,dl_type=0x0806,nw_dst=10.0.0.{1},actions=output:"{switch}-eth{nSwitches-1}"'
			print(cmd)
			os.system(cmd)
		for j in range(1,nHosts+1):
			target = findSwitch(j,sRanges)
			if target == i:
				offset1 = hSwitches - 1
				offset2 = j - hSwitches*i
				position = offset1 + offset2 + offset0
				cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=60,priority=100,dl_type=0x0800,nw_dst=10.0.0.{j+1},actions=output:"{switch}-eth{position}"'
				print(cmd)
				os.system(cmd)
				cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=60,priority=100,dl_type=0x0806,nw_dst=10.0.0.{j+1},actions=output:"{switch}-eth{position}"'
				print(cmd)
				os.system(cmd)
			else:
				position = orderDict[target]
				cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=60,priority=100,dl_type=0x0800,nw_dst=10.0.0.{j+1},actions=output:"{switch}-eth{position}"'
				print(cmd)
				os.system(cmd)
				cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=60,priority=100,dl_type=0x0806,nw_dst=10.0.0.{j+1},actions=output:"{switch}-eth{position}"'
				print(cmd)
				os.system(cmd)
				

def findSwitch(node, sRanges):
	i = 0
	for _ in range(len(sRanges)):
		if node in sRanges[i]:
			break
		i+=1
	return i
			
def orderSwitches(s, nSwitches):
	orderDict = {}
	counter = 1
	for i in range(nSwitches):
		if i != s:
			orderDict[i] = counter
			counter += 1
	return orderDict

def meshTopo(nHosts, hostBand, hostQueue, hostDelay, hostLoss):
	"Fully connected switches connected to n/s hosts."
	hSwitches = round(nHosts**(1/2)+0.5)
	
	links = set()
	i = 0
	j = 0
	while i < nHosts:
		s = "s"+str(j)
		while i < nHosts:
			h = "h"+str(i+1)
			link = frozenset([h,s])
			links.add(link)
			i+=1
			if (i%hSwitches)==0:
				break
		j+=1
	links.add(frozenset(["h0",s]))
	
	nSwitches = j
	switches = []
	for s in range(nSwitches):
		switches.append("s"+str(s))
	
	hosts = ["h"+str(i) for i in range(nHosts+1)]
	hostDict = distributeHosts(hosts, switches, links, hostBand, hostQueue, hostDelay, hostLoss)

	links = set()
	for s1 in switches:
		for s2 in switches:
			if s1 != s2:
				links.add(frozenset([s1,s2]))
					
	netDict = createDictSwitches(switches,links)
	
	outDict = {}
	outDict["networks"] = netDict
	outDict["peers"] = hostDict
	
	return outDict, nSwitches
	

def createDictSwitches(switches, links):
    
	''' Creates a the network topo defined by edges'''

	netOutput = {}

	done = set()
	for s1 in switches:
		done.add(s1)

		edges = {}
		for s2 in done:
			if getParam(s1,s2,links):
				edges[s2] = {"loss":0}

		netOutput[s1] = None

		if len(edges) != 0:
			netOutput[s1] = edges

	return netOutput

def distributeHosts(hosts, switches, links, hostBand, hostQueue, hostDelay, hostLoss):
	hostOutput = {}

	for h in hosts:
		for s in switches:
			if {h,s} in links:
				hostOutput[h] = {s: {
					"bw": hostBand,
					"delay": hostDelay,
					"loss": hostLoss,
					"max_queue_size": hostQueue
				}}

	return hostOutput

def getParam(s1, s2, links):
	if {s1,s2} in links:
		return True
	return False

		
def simpleTest(inputPath, configPath):

	call(["mn","-c"])
	
	# Read input file
	with open(inputPath, 'r') as myfile:
		data = myfile.read()
		
	obj = json.loads(data)

	numberNodes = obj['parameters']['n']

	with open(configPath, 'r') as confFile:
		sim_conf =  confFile.read()

	# parse file
	sim_conf = json.loads(sim_conf)

	# read topo file
	#pathTopoFile = "Topos/" + sim_conf["topology"]

	#with open(pathTopoFile, 'r') as topoFile:
	#	net_topo =  topoFile.read()

	# parse file
	#net_topo = json.loads(net_topo)
	
	#fullTopo = generateMininetTopo(net_topo, numberNodes+1, sim_conf["hostBand"], 
	#			sim_conf["hostQueue"], sim_conf["hostDelay"], sim_conf["hostLoss"])
	
	fullTopo, nSwitches = meshTopo(numberNodes, sim_conf["hostBand"], sim_conf["hostQueue"],
				 sim_conf["hostDelay"], sim_conf["hostLoss"])

	print("-------------------------------------------")
	print(fullTopo)
	print("-------------------------------------------")
	"Create and test a simple network"
	topo = CustomTopo(fullTopo, sim_conf["testNodes"])
	#net = Mininet(topo, host=CPULimitedHost, link=TCLink)
	net = Mininet(topo, link=TCULink, build=False, waitConnected=False)
	net.addController( RemoteController( 'c0', ip='127.0.0.1', port=6633 ))
	net.build()
	
	try:
		net.start()
		
		print( "Dumping switch connections" )
		dumpNodeConnections(net.switches)
		"""
		switch = 's0'

		for i in range(1,numberNodes+2):
			cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=60,priority=100,dl_type=0x0800,nw_dst=10.0.0.{i},actions=output:"{switch}-eth{i}"'
			print(cmd)
			os.system(cmd)
			cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=60,priority=100,dl_type=0x0806,nw_dst=10.0.0.{i},actions=output:"{switch}-eth{i}"'
			print(cmd)
			os.system(cmd)

		os.system(f"ovs-ofctl dump-flows {switch}")
		"""
		meshRules(numberNodes, nSwitches)
		
		print( "Setting up main server" )
		hosts = net.hosts
		
		popens = {}
		#threads = []

		# server execution code
		cmd = "./mainserver --n " + str(numberNodes) + " --log_file outputs/mainOut.txt"
		popens[hosts[0]] = hosts[0].popen(cmd)
		print(inputPath + ", " + configPath)

		sleep(.1) # time to setup main server

		print( "Setting up nodes" )

		for i in range(numberNodes):
		
			# node execution code
			nodeId = str(i)
			inputFile = "--input_file " + inputPath
			logFile = "--log_file outputs/process" + nodeId + ".txt"	
			#nTr = "--transactions " + str(sim_conf["numberTransactions"])
			#trDelay = "--transaction_init_timeout_ns " + str(sim_conf["transactionDelay"])
			
			#cmd = "./node " + inputFile + " " + logFile + " --i " + nodeId + " " + nTr + " " + trDelay + " 2>&1"
			cmd = "./node " + inputFile + " " + logFile + " --i " + nodeId  + " 2>&1"

			popens[hosts[i+1]] = hosts[i+1].popen(cmd, shell=True)
			
			#os.system(f"timeout 10 tcpdump -i s0-eth{i+1} -i  s0-eth{i}")

		
		# CPU test node, allow checking if nodes are getting enough CPU time
		#selfTest = hosts[1]
		#selfTest.cmd("bash selfControl.sh > outputs/selfControl.txt 2>&1 &")
		
		offset = 0
		hTestIn = net.get('h0')
		hTestOut = net.get('h0')
		if sim_conf["testNodes"]["inTestNodes"]:
			hTestIn = net.get('h' + str(numberNodes+1))
			hTestIn2 = net.get('h' + str(numberNodes+2))
			hTestIn.cmd("ping " + hTestIn2.IP() + " > outputs/inControl.txt 2>&1 &")
			offset += 2
			
		if sim_conf["testNodes"]["outTestNodes"]:
			hTestOut = net.get('h' + str(numberNodes+1+offset))
			hTestOut2 = net.get('h' + str(numberNodes+2+offset))
			hTestOut.cmd("ping " + hTestOut2.IP() + " > outputs/outControl.txt 2>&1 &")
			
		print("Simulation start... ")
		#os.system("timeout 10 tcpdump -i  s0-eth1")
		info( "Monitoring output for", sim_conf["simulationTime"], "seconds\n" )
		endTime = time() + sim_conf["simulationTime"]
		for h, line in pmonitor( popens, timeoutms=100 ):
			if h:
				info( '<%s>: %s' % ( h.name, line ) )
			if time() >= endTime:
				print("Sending termination signal...")
				for p in popens.values():
					p.send_signal( SIGINT )
				break
		#sleep(sim_conf["simulationTime"])
		print("Simulation end... ")

		#selfTest.cmd("kill %bash")
		hTestIn.cmd("kill %ping")
		hTestOut.cmd("kill %ping")
		#for p in popens.values():
		#	p.send_signal(SIGINT)
		
		net.stop()
		
	finally:
		call("sudo pkill -f node", shell = True)
		call("sudo pkill -f mainserver", shell = True)
		call(["mn","-c"])
		
		print("Compressing outputs...")
		firstName = inputPath.split("/")[-1]
		lastName = configPath.split("/")[-1]
		fileName = "outputs/compressed/" + firstName.split(".")[0] + lastName.split(".")[0] + ".tar.gz"
		listFiles = ["tar","-czf",fileName,"outputs/mainOut.txt"]
		if sim_conf["testNodes"]["inTestNodes"]:
			listFiles.append("outputs/inControl.txt")
		if sim_conf["testNodes"]["outTestNodes"]:
			listFiles.append("outputs/outControl.txt")
		#listFiles.append("outputs/selfControl.txt")
			
		for i in range(numberNodes):
			listFiles.append(f"outputs/process{i}.txt")
			
		# Compressing files
		call(listFiles)

	
		print("The end")

if __name__ == '__main__':
	"""
		Usage: sudo python3 launch.py inputPath configPath
	"""
	# Tell mininet to print useful information
	setLogLevel('info')
	simpleTest(sys.argv[1], sys.argv[2])
