#!/usr/bin/env python
# coding: utf-8

import json
import random

def createOutDict(netTopo, nHosts, hostBand, hostQueue, hostDelay, hostLoss):
    
    ''' Creates a random distribution of hosts over the network topo'''

    output = {}       
    output["networks"] = netTopo
    output["peers"] = distributeHosts(len(netTopo), nHosts, hostBand, hostQueue, hostDelay, hostLoss)
    
    return output

def distributeHosts(nSwitches, nHosts, hostBand, hostQueue, hostDelay, hostLoss):
    
    hostOutput = {}
    
    for j in range(nHosts):
        server = "s" + str(random.randrange(nSwitches))
        host = "h" + str(j)
        link = {
            "bw": hostBand,
            "delay": hostDelay,
            "loss": hostLoss,
            "max_queue_size": hostQueue
        }
        hostOutput[host] = {server: link}
    
    return hostOutput

def generateMininetTopo(nHosts):
    
    # read config file
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

    # Creates a dictionary with full information about the topology
    fullTopo = createOutDict(net_topo, nHosts, sim_conf["hostBand"], 
                             sim_conf["hostQueue"], sim_conf["hostDelay"], sim_conf["hostLoss"])
    
    return fullTopo

    # Serializing json
    #json_object = json.dumps(fullTopo, indent=4)

    # Writing to sample.json
    #with open("networkTopo.json", "w") as outfile:
    #    outfile.write(json_object)
