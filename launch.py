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
	def build(self, net_topo):
		
		switches = {}
		for net in net_topo['networks'].keys():
			switches[net] = self.addSwitch(net)
			
			if net_topo['networks'][net] != None:
				for net_ in net_topo['networks'][net].keys():
					args = net_topo['networks'][net][net_]
					self.addLink(net, net_,**args)
				
		for peer in net_topo['peers'].keys():
			self.addHost(peer)
			for net_ in net_topo['peers'][peer].keys():
				args = net_topo['peers'][peer][net_]
				self.addLink(peer, net_,**args)

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
	topo = CustomTopo(fullTopo)
	net = Mininet(topo, host=CPULimitedHost, link=TCLink)
	net.start()

	#print( "Dumping host connections" )
	#dumpNodeConnections(net.hosts)

	print( "Dumping switch connections" )
	dumpNodeConnections(net.switches)
	
	print( "Setting up main server" )
	hosts = net.hosts

	popens = {}

	# server execution code
	cmd = "./mainserver --n " + str(numberNodes) + " --log_file outputs/mainOut.txt"
	popens[hosts[0]] = hosts[0].popen(cmd)
	print(cmd)

	sleep(1) # time to setup main server

	print( "Setting up nodes" )

	for i in range(numberNodes):
		# node execution code
		nodeId = str(i)
		cmd = "./node --input_file ConfigFiles/input.json --log_file outputs/process" + nodeId + ".txt --i " + nodeId + " --transactions 5 --transaction_init_timeout_ns 1000000000"
		popens[hosts[i+1]] = hosts[i+1].popen(cmd)
		#print(cmd)
		
	print("Simulation start... ")
	sleep(sim_conf["simulationTime"])
	print("Simulation end... ")

	for p in popens.values():
		p.send_signal(SIGINT)
	
	sleep(10)
	
	print("The end")

	net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
