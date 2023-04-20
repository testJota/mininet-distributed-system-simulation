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

def generateMininetTopo(net_topo,nHosts,hostBand,hostQueue,hostDelay,hostLoss):
    

    # Creates a dictionary with full information about the topology
    fullTopo = createOutDict(net_topo,nHosts,hostBand,hostQueue,hostDelay,hostLoss)
    
    return fullTopo

    # Serializing json
    #json_object = json.dumps(fullTopo, indent=4)

    # Writing to sample.json
    #with open("networkTopo.json", "w") as outfile:
    #    outfile.write(json_object)
