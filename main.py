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
import dynamics.traffic_models.ltaModelMaker as lta
from matplotlib import pyplot as plt
from datetime import datetime


if __name__ == "__main__":
    # Useful Paths
    datapath = "/home/louis/Documents/Research/Code/foo-Environment_2/dynamics/demand_models/"
    curPath = os.path.abspath(os.curdir)

    # files_speed_band = os.listdir('/media/louis/WIN10OS/Users/e0022825/Documents/Research/dataSpeedBandLTA')

    # load delivery data
    deliverydata = np.loadtxt(datapath + "fedex.data")
    mask = deliverydata[:, 0] == 2122015  # 2 dec 2015
    deliverydata = deliverydata[mask]

    deliverydata = deliverydata[123:156, :]  # 4th truck (we removed the first task because of data paucity)
    print(len(deliverydata))
    # class instance
    instance1 = foo_env.FooEnv(deliverydata, '1022')
    # Initialize
    instance1.reset()
    serviceTime = deliverydata[:, 3]
    timeGap = []
    FMT = '%H%M'

    #instance1.time = '1410'


    #durations = instance1.traveltimereader()
    #print(len(durations[17]))




    # a: index of the place to visit (action) in the FedEx order !
    a = 1
    while (not instance1.done):

        # adapt the FedEx actions to the tasks order
        a_new = np.argwhere(  instance1.tasks[:, 4] == instance1.deliverydata[a, 4] )

        # case with 2 similar addresses
        a_new =  int(a_new[0]) if instance1.visited_customer[int(a_new[0])] == 0 else int(a_new[1])
        print("action ", a)
        s, reward, done, info = instance1.step(a_new)
        if info == 'Lunch break':

            # replay this same action !
            instance1.render()
            instance1.step(a_new)
        a += 1
            # break
        instance1.render()
        print("Total number of known tasks ", instance1.tasks[:, 3].size)

        print('_' * 50)
        print('_' * 50)
        print('_' * 50)

        # print(instance1.time)
        # print(str(serviceTime[a]))
        # tdelta =  datetime.strptime(str(int(serviceTime[a])), FMT) - datetime.strptime(instance1.time, FMT)
    #     print(tdelta.seconds)
    #     timeGap.append(tdelta.seconds /60)
    # plt.scatter(range(len(timeGap)), timeGap)
    # plt.show()

