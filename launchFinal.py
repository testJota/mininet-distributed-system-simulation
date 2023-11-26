#!/usr/bin/python                                                                            
    
import sys
from subprocess import call
from time import time                   
from time import sleep
import json
from signal import SIGINT
import os
                                                                                             
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.link import TCULink
from mininet.util import pmonitor
from mininet.node import Controller, RemoteController
from mininet.cli import CLI

from generateTreeTopo import createTreeTopo

class CustomTopo(Topo):
    "Creates a customized topology based on net_topo."
    def build(self, net_topo):

        for net in net_topo['networks'].keys():
            self.addSwitch(net)
            for net_ in net_topo['networks'][net].keys():
                args = net_topo['networks'][net][net_]
                self.addLink(net, net_,**args)

        n = len(net_topo['peers'].keys())
        for peer in net_topo['peers'].keys():
            self.addHost(peer)
            for net_ in net_topo['peers'][peer].keys():
                args = net_topo['peers'][peer][net_]
                self.addLink(peer, net_,**args)

def defineTreeRules(net,n_leaves,max_children):
    '''
        Adds rules to the switches of a pre-defined network tree topology.
        The tree has 32 leaves, which are mininet nodes running the protocol processes.
        Each switch has 4 childrens, which means that the lowest layer of switches has 8 switches.
    '''

    hosts = net.hosts
    switches = net.switches

    endIp = 0
    for h in hosts:
        endIp = endIp + 1
        lowSubnet = int((endIp-1) // (max_children))
        upSubnet = int((endIp-1) // (max_children**2))

        hostIp = "10." + str(upSubnet) + "." + str(lowSubnet) + "." + str(endIp)

        h.setIP(hostIp)
        print(hostIp)

    for i in range(4):
        switch = switches[i]

        for s in switches:
            link = switch.connectionsTo(s)
            if link:
                l = link[0][0]
                cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst=10.1.0.1/16,actions=output:"{l}"'
                print(cmd)
                os.system(cmd)
                cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst=10.1.0.1/16,actions=output:"{l}"'
                print(cmd)
                os.system(cmd)

                for j in range(4):
                    if j != i:
                        cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst=10.0.{j}.1/24,actions=output:"{l}"'
                        print(cmd)
                        os.system(cmd)
                        cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst=10.0.{j}.1/24,actions=output:"{l}"'
                        print(cmd)
                        os.system(cmd)

        for h in hosts:
            link = switch.connectionsTo(h)
            if link:
                ip = h.IP()
                l = link[0][0]
                cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst={ip},actions=output:"{l}"'
                print(cmd)
                os.system(cmd)
                cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst={ip},actions=output:"{l}"'
                print(cmd)
                os.system(cmd)

    for i in range(4,8):
        switch = switches[i]

        for s in switches:
            link = switch.connectionsTo(s)
            if link:
                l = link[0][0]
                cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst=10.0.0.1/16,actions=output:"{l}"'
                print(cmd)
                os.system(cmd)
                cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst=10.0.0.1/16,actions=output:"{l}"'
                print(cmd)
                os.system(cmd)

                for j in range(4,8):
                    if j != i:
                        cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst=10.1.{j}.1/24,actions=output:"{l}"'
                        print(cmd)
                        os.system(cmd)
                        cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst=10.1.{j}.1/24,actions=output:"{l}"'
                        print(cmd)
                        os.system(cmd)

        for h in hosts:
            link = switch.connectionsTo(h)
            if link:
                ip = h.IP()
                l = link[0][0]
                cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst={ip},actions=output:"{l}"'
                print(cmd)
                os.system(cmd)
                cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst={ip},actions=output:"{l}"'
                print(cmd)
                os.system(cmd)

    for i in range(8,10):
        switch = switches[i]
        up = i % 8
        down = 1-up

        for j in range(8):
            link = switch.connectionsTo(switches[j])
            if link:
                l = link[0][0]
                cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst=10.{up}.{j}.1/24,actions=output:"{l}"'
                print(cmd)
                os.system(cmd)
                cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst=10.{up}.{j}.1/24,actions=output:"{l}"'
                print(cmd)
                os.system(cmd)

        link = switch.connectionsTo(switches[10])
        l = link[0][0]
        cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst=10.{down}.0.1/16,actions=output:"{l}"'
        print(cmd)
        os.system(cmd)
        cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst=10.{down}.0.1/16,actions=output:"{l}"'
        print(cmd)
        os.system(cmd)

    switch = switches[10]
    link = switch.connectionsTo(switches[8])
    l = link[0][0]
    cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst=10.0.0.1/16,actions=output:"{l}"'
    print(cmd)
    os.system(cmd)
    cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst=10.0.0.1/16,actions=output:"{l}"'
    print(cmd)
    os.system(cmd)
    link = switch.connectionsTo(switches[9])
    l = link[0][0]
    cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0800,nw_dst=10.1.0.1/16,actions=output:"{l}"'
    print(cmd)
    os.system(cmd)
    cmd = f'ovs-ofctl add-flow {switch} table=0,idle_timeout=300,priority=100,dl_type=0x0806,nw_dst=10.1.0.1/16,actions=output:"{l}"'
    print(cmd)
    os.system(cmd)


    os.system(f"ovs-ofctl dump-flows {switch}")

def systemSimulation(inputPath, configPath):

    "Create and test a tree network. The degree of each node is limited to 4."
    n_leaves = 32
    max_children = 4

    # Read input file
    with open(inputPath, 'r') as myfile:
        data = myfile.read()

    obj = json.loads(data)
    nHosts = obj['parameters']['n']

    # Read config file
    with open(configPath, 'r') as confFile:
        sim_conf =  confFile.read()

    # parse file
    sim_conf = json.loads(sim_conf)

    fullTopo = createTreeTopo(n_leaves, max_children=max_children, hostBand=sim_conf["hostBand"], hostQueue=sim_conf["hostQueue"],
                 hostDelay=sim_conf["hostDelay"], hostLoss=sim_conf["hostLoss"])
    topo = CustomTopo(fullTopo)

    call(["mn","-c"])
    net = Mininet(topo, link=TCULink, build=False, waitConnected=False)
    net.addController( RemoteController( 'c0', ip='127.0.0.1', port=6633 ))
    net.build()

    try:
        net.start()

        print( "Dumping switch connections" )
        dumpNodeConnections(net.switches)

        print( "Setting up network switches" )
        defineTreeRules(net,n_leaves,max_children)

        print( "Setting up main server" )
        hosts = net.hosts

        popens = {}

        # server execution code
        cmd = f"./mainserver --n {nHosts} --log_file outputs/mainOut.txt --topo tree --nodes {n_leaves}"
        popens["Main"] = hosts[nHosts % n_leaves].popen(cmd)
        print(inputPath + ", " + configPath)

        sleep(1) # time to setup main server

        print( "Setting up nodes" )

        clientSet = set([x for x in range(n_leaves//2)])

        for i in range(nHosts):
            # node execution code

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

            cmd = f"./node --input_file {inputPath} --log_file outputs/process{i}.txt --i {i} {nTr} {trDelay} --topo tree --nodes {n_leaves} 2>&1"

            #cmd = "./node " + inputFile + " " + logFile + " --i " + nodeId  + " 2>&1"
            #popens[hosts[i+1]] = hosts[i+1].popen(cmd, shell=True)

            popens[str(i)] = hosts[i % n_leaves].popen(cmd, shell=True)

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
        Usage: sudo python3 launchTree_test.py number_of_Hosts
    """
    # Tell mininet to print useful information
    setLogLevel('info')
    systemSimulation(sys.argv[1], sys.argv[2])
