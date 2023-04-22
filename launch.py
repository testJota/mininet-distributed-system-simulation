#!/usr/bin/python                                                                            
                                   
from time import sleep
from signal import SIGINT
import json
from subprocess import call
                                                                                             
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import CPULimitedHost
from mininet.link import TCLink

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
				
		for peer in net_topo['peers'].keys():
			self.addHost(peer)
			for net_ in net_topo['peers'][peer].keys():
				args = net_topo['peers'][peer][net_]
				self.addLink(peer, net_,**args)
		
		numberHosts = len(net_topo['peers'].keys())
		if testNodes["inTestNodes"]:
			numberSwitches = len(net_topo['networks'].keys())
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
		
def simpleTest():

	call(["mn","-c"])
	
	# Read input file
	with open('ConfigFiles/input.json', 'r') as myfile:
		data = myfile.read()
		
	obj = json.loads(data)

	numberNodes = obj['parameters']['n']
	
	# Read simulation conf file
	pathConf = "ConfigFiles/simulation_conf.json"

	with open(pathConf, 'r') as confFile:
		sim_conf =  confFile.read()

	# parse file
	sim_conf = json.loads(sim_conf)

	# read topo file
	pathTopoFile = "Topos/" + sim_conf["topology"]

	with open(pathTopoFile, 'r') as topoFile:
		net_topo =  topoFile.read()

	# parse file
	net_topo = json.loads(net_topo)
	
	fullTopo = generateMininetTopo(net_topo, numberNodes+1, sim_conf["hostBand"], 
				sim_conf["hostQueue"], sim_conf["hostDelay"], sim_conf["hostLoss"])

	"Create and test a simple network"
	topo = CustomTopo(fullTopo, sim_conf["testNodes"])
	net = Mininet(topo, host=CPULimitedHost, link=TCLink)
	net.start()
	
	print( "Dumping switch connections" )
	dumpNodeConnections(net.switches)
	
	print( "Setting up main server" )
	hosts = net.hosts

	popens = {}

	# server execution code
	cmd = "./mainserver --n " + str(numberNodes) + " --log_file outputs/mainOut.txt"
	popens[hosts[0]] = hosts[0].popen(cmd)
	print(cmd)

	sleep(.1) # time to setup main server

	print( "Setting up nodes" )

	for i in range(numberNodes):
	
		# node execution code
		nodeId = str(i)
		inputFile = "--input_file ConfigFiles/input.json"
		logFile = "--log_file outputs/process" + nodeId + ".txt"	
		nTr = "--transactions " + str(sim_conf["numberTransactions"])
		trDelay = "--transaction_init_timeout_ns " + str(sim_conf["transactionDelay"])
		
		cmd = "./node " + inputFile + " " + logFile + " --i " + nodeId + " " + nTr + " " + trDelay
		popens[hosts[i+1]] = hosts[i+1].popen(cmd)
	
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
	sleep(sim_conf["simulationTime"])
	print("Simulation end... ")

	hTestIn.cmd("kill %ping")
	hTestOut.cmd("kill %ping")
	for p in popens.values():
		p.send_signal(SIGINT)
	
	sleep(10)
	
	print("The end")
	
	"""
	print( "Setting up test nodes" )
	h1 = net.get('h1')
	h1.cmd("ping 10.0.0.1 > control.txt 2>&1 &")
	sleep(10)
	print( "Stopping test" )
	h1.cmd("kill %ping")
	"""

	net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
