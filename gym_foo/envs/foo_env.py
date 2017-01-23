# -*- coding: utf-8 -*-
"""
Created on Wed Jan  11 10:10:58 2017

@author: Louis DOUGE
"""
import json
import urllib.parse
from urllib.parse import urlparse
import httplib2 as http #External library

import numpy as np
import itertools as it

import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym.envs.toy_text import discrete

def dataRetriever():
    #Authentication parameters
    headers = { 'AccountKey' : '6HsAmP1e0R/EkEYWOcjKg==',
               'accept' : 'application/json'} #this is by default
               
    #API parameters
    uri = 'http://datamall2.mytransport.sg/' #Resource URL 
    path = '/ltaodataservice/TrafficIncidents?'
    
    #Build query string & specify type of API call
    target = urlparse(uri + path) 
    print(target.geturl())
    method = 'GET'
    body = ''
    #Get handle to http
    h = http.Http()
    #Obtain results
    response, content = h.request(
        target.geturl(),
        method,
        body,
        headers)
    #Parse JSON to print
    jsonObj = json.loads(content)
    print(json.dumps(jsonObj, sort_keys=True, indent=4))
    #Save result to file
    with open("traffic_incidents.json","w") as outfile: 
        #Saving jsonObj["d"]
        json.dump(jsonObj, outfile, sort_keys=True, indent=4,
              ensure_ascii=False)

# Functions working on data
def travelTime(node1,node2,t):
    """
    Return the mean and variance of the travel time necessary to go from node1 to node2 at time t
    """
    
    #Retrieve the data (could be shared with probCongStatus too)
    
    #Identify road segments
    
    #Compute the travel time mean for each segment and then sum
    
    return 0

def probCongStatus(node1,node2,t):
    """
    Return the probabilities of the congestion status after traveling from 
    node1 to node2 at time t, for all the arcs?
    """
    
    return 0

class FooEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        
        ## Attributes
        
        """
        Later: should be imported from a fixed format file to be reused everyday
        """
        
        #Number of location to visit
        self.nL=10
        #Number of ways to classify congestion traffic on one arc
        # ex: nC=2 => traffic on one arc classified as non-jammed or jammed
        self.nC=2
        
        # Known customer locations
        self.custLoc={a : [] for a in range (nL)}
        
        # Unknow customer locations
        # to be included: probability distribution of pick-ups to pop up
        
        #Dynamics for traffic congestion
        self.P = {s : {a : [] for a in range(nA)} for s in range(nS)} 
        
        #Dynamics for travel time estimation
        #We need to retrieve the mean and variance of the considered arc
        
        #Action space: nL*(nL-1) possible action, but given a state only some of them
        # are doable
        #self.action_space=it.permutations(range(nL),2)
        #Observation space: too large and we're not going to visit all the nodes...
        #self.observation_space=2
        


        
        
        
           
    
    def _step(self, action):
        #Reward Computations first
        #Reward: expectancy of the cost function to do the action ie mean of travel time
        reward=travelTime(self.curNode,action,self.time)
    
        
        #Next state computations second
        self.time+=1
        self.curNode=action
        self.remNodes[action]=1
        self.congStatus=probCongStatus(self.curNode, action, self.time)
        self.remNodes[self.curNode]=1
        
        self.state= self.time, self.node, self.congStatus, self.remNodes
        
        #Are we done ?
        if(self.remNodes==np.ones(self.nL)):
            done=True
        else:
            done=False
        
        return self.state, reward, done
    
    def _reset(self):
        
        #
        self.time=0

        #
        self.curNode=0

        #
        self.congStatus=np.zeros((self.nL,self.nL))     
        
        #Remaining nodes: visited 1, non-visited 0 
        self.remNodes=np.zeros(self.nL)
        
        # Start at the beginning (depot node): node, time, congestion status, remaining nodes
        #Originally no traffic - STORE IT ??
        self.state= self.time, self.node, self.congStatus, self.remNodes
        
        return self.state
        
    def _render(self, mode='human', close=False):
        ...

