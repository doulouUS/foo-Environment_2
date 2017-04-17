#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 13:41:00 2017

@author: Louis
"""
import sys
sys.path.append('/home/louis/Documents/Research/Code/foo-Environment_2/dynamics') # add the path of gym-foo directory

import schedule
import time
import os

# Math modules
import numpy as np

# Homemade modules
import dynamics.fooTools as fooTools
import dynamics.demand_models.demandModels as dMod
import gym_foo.envs.foo_env as foo_env

# Agents import
from Agents.agent_0_fedex import agent_0_fedex as ag0 # FedEx
import Agents.agent_1_MC as ag1
import dynamics.traffic_models.ltaModelMaker as lta
from matplotlib import pyplot as plt
from datetime import datetime


if __name__ == "__main__":
    # Useful Paths
    datapath_lin = "/home/louis/Documents/Research/Code/foo-Environment_2/dynamics/demand_models/"
    datapath_mac = "/Users/Louis/PycharmProjects/MEng_Research/foo-Environment_2/dynamics/demand_models/"
    curPath = os.path.abspath(os.curdir)

    # files_speed_band = os.listdir('/media/louis/WIN10OS/Users/e0022825/Documents/Research/dataSpeedBandLTA')

    # -------------------- load scenario----------------------------------

    # TODO add a line for the depot

    # to run on either machine
    if sys.platform == 'linux':
        deliverydata = np.loadtxt(datapath_lin + "fedex.data")
    elif sys.platform == 'darwin':
        deliverydata = np.loadtxt(datapath_mac + "fedex.data")

    mask = deliverydata[:, 0] == 2122015  # 2 dec 2015
    deliverydata = deliverydata[mask]

    deliverydata = deliverydata[123:156, :]  # 4th truck (we removed the first task because of data paucity)
    # print(len(deliverydata))

    # -------------------- class instance and configuration--------------------
    instance1 = foo_env.FooEnv(deliverydata, startTime='1022', servTime=6.5)

    # Initialize
    instance1.reset()
    serviceTime = deliverydata[:, 3]
    timeGap = []
    FMT = '%H%M'

    # -------------------- Run agent on scenario --------------------
    # Alg0 Fedex real case
    # ag0(instance1)

    # Retrieve the State
    state0 = ag1.state(instance1)
    #print("Loc", state0.loc)
    # print("Time", state0.time)
    #print("Cust", state0.remCustomers)

    # Model the pickup

    # Create the agent
    agent = ag1.agent1(state=state0,  t_range=12*60, bandwidth=100)
    # Tests
    start = time.time()
    agent.cost_to_go_mc()
    end = time.time()

    print("Time elapsed", end - start)



    # Alg1 on retrieved state
    # Creation of an agent
    #agent = ag1(instance1, bandwdth=80)
    #mean, std = agent.mean_pi(5)
    #print(mean, std)


