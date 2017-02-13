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
import math
import itertools as it

import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym.envs.toy_text import discrete

from dynamics.fooTools import roadSegments
import pickle # loading binary files containing data
import time
import csv
import os
import schedule
from re import split

def timeupdate(string, timestep):
    """

    :param string 'HHmm', timestep integer
    :return: string updated 'HHmm'
    """
    update = int(string) + timestep
    if update < 1000:
        update = '0' + str(update)

    return update

class FooEnv(gym.Env):

    metadata = {'render.modes': ['human']}

    def __init__(self, deliverydata):
        """


        :param deliverydata: np array     ['StopDate','WeekDay','StopOrder','StopStartTime','Address','PostalCode',
            'CourierSuppliedAddress','ReadyTimePickup','CloseTimePickup','PickupType',
            'WrongDayLateCount','RightDayLateCount','FedExID','Longitude','Latitude']

            /!\ Make sure the first line of this array is the depot /!\

        """
        self.deliverydata = deliverydata
        # LOCATION RELATED
        # FedEx data
        self.locations = deliverydata[:, 4]  # Addresses ID

        # Delivery locations to visit
        self.mask_d = self.deliverydata[:, 7] == 0  # deliveries
        self.deliveryLocations = self.deliverydata[self.mask_d][:, 4]  # ID of the delivery locations
        self.ndl = np.size(self.deliveryLocations)  # Number of delivery locations

        # Pick-up locations to visit : invisible to the agent (pre-loaded scenario)
        self.mask_p = self.deliverydata[:, 7] != 0
        self._pickupLocations = self.deliverydata[self.mask_p][:, 4]  # ID of the pickup addresses
        self._npl = np.size(self._pickupLocations)  # Number of pickup locations

        # TRAFFIC RELATED
        # datapath containing the travel duration time
        self.pathTravelDuration = '/home/louis/Documents/Research/Code/foo-Environment_2/gym_foo/envs/' \
                                  'travel_duration_data/'

        # TIME RELATED
        # Time of appearance of the pickup locations
        self._pickupTime = self.deliverydata[self.mask_p][:, 7]

        # Duration of one time step in mn
        self.timeStep = 30

        # Start of operations
        self.startTime = '0800'  # 8am

        # STATE RELATED
        # Number of ways to classify congestion traffic on one arc
        # ex: nC=2 => traffic on one arc classified as non-jammed (0) or jammed (1)
        self.nC = 2

        # Define the state, see _reset() for a meaningful initialization
        self.time = "0"
        self.currentLocation = 0
        self.durations = []
        self.customerState = 0

        self.s = self.time, self.currentLocation, self.durations, self.customerState

    def _reset(self):
        """
            Initialize the state

        :return: tuple
        """
        # End Status
        self.done = False

        # Last action
        self.lastAction = -1

        # Tasks to be accomplished
        self.tasks = self.deliverydata[self.mask_d]
        self._tasksAhead = self.deliverydata[self.mask_p]

        self.time = self.startTime
        self.currentLocation = self.deliveryLocations[0]  # First Address: depot
        try:
            # Read file corresponding to the current time (here self.starttime)
            with open(self.pathTravelDuration+self.closesttraveldurationfile(), 'rb') as fp:
                self.durations = pickle.load(fp)
        except:
            print("WARNING: Setting durations to an empty list because error on travel duration retrieval")
            self.durations = []

        self.customerState = self.ndl * [0]  # No customer serviced yet,
        #  only deliveries are known at the beginning. this object gives an ID to the jobs (their index) to be done

        return self.s

    def _step(self, a):
        """
            Give the next state and reward

        :param: a, action. ID of the location to visit, based on self.customerState
        :return: state, reward, done or not, info
        """
        if (a < self.tasks.shape[0]) & (not self.done):
            # STATE
            # Increase time
            self.time = timeupdate(self.time,self.timeStep)

            # Update locations to visit: new demand maybe !
            # Update current tasks
            mask_update = self.time > self._tasksAhead[:, 7]
            newTasks = self._tasksAhead[mask_update]
            self.tasks = np.concatenate((self.tasks, newTasks), axis=0)  # Add the new jobs

            # Congestion Status
            try:
                # Read file corresponding to the current time
                with open(self.pathTravelDuration + self.closesttraveldurationfile(), 'rb') as fp:
                    self.durations = pickle.load(fp)
            except:
                print("WARNING: Setting durations to an empty list because error on travel duration retrieval")
                self.durations = []

            # Update customerState, if not the first move
            if self.lastAction != -1:
                self.customerState[a] = 1  # due to the action a is visited

            self.customerState += newTasks.shape[0] * [0]  # Add the status of these new jobs

            # Current location
            self.currentLocation = self.tasks[a, 4]  # Address

            self.lastAction = a

            # REWARD: traveling time from lastAction to a (or depot to a if starting)
            reward = self.reward()

            # END STATUS
            if (len(self.customerState) - 1) * [1] in self.customerState:
                self.done = True

            # INFO
            info = "A useful info please"

            return self.s, reward, self.done, info

        else:
            print("Action not available or End of operations")


    def _render(self, mode='human', close=False):
        ...

    def infolinks(self):
        """
            Two approaches:
                1. Congestion status is based on data retrieved using bing API
                    => function return global travel time

                2. Congestion status is based on speed band data (inaccurate right now)
                    => function return speed on considered road segments, allowing us to
                        compute the travel time

        :return: tuple, shape 3, list of list: roads, coordPaths, travelDurations between all locations
        """

        """OPTION 2.
        # Load data
        maxspeed = np.loadtxt('/home/louis/Documents/Research/Code/foo-Environment_2/dynamics/traffic_models'
                              '/maxSpeedBand_09h20-25-01-2017_to_10h30-31-01-2017.gz', dtype=int)

        # Retrieve the right date and time TODO include the date choice as a function parameter
        mask_time = maxspeed[:, 0] == int("20172601" + self.time)
        maxspeed = maxspeed[mask_time]
        """
        """OPTION 1."""
        # road links we are interested in
        roads = [] # contains all the roads to link every locations to be visited (~triangular sup matrix)
        coordPaths = [] # "     "       route coordinates
        travelDurations = []  # " " the travel durations

        for idxStart in range(self.locations.size - 1):
            subroad = [] # contains all the roads starting from idxStart
            subcoordPaths = []
            subtravelDuration = []

            for idxEnd in range(idxStart + 1, self.locations.size):
                # Retrieve string addresses of locations to visit
                with open('/home/louis/Documents/Research/Code/foo-Environment_2/gym_foo/envs/addresses.fedex', 'rb') as fp:
                    addresses = pickle.load(fp)
                    location1 = addresses[int(self.locations[idxStart])]
                    location2 = addresses[int(self.locations[idxEnd])]
                    # print(location1)
                    # print(location2)
                # Route
                statusCode, travdistance, travdur, travelDurationTraffic, nbSegments, roadName, \
                travdistances, travdurs, maneType, pathCoord = roadSegments([location1+' Singapore', location2+' Singapore'])

                # print("No traffic travel time")
                # print(travdur)

                # print("Traffic travel time")
                # print(travelDurationTraffic)

                subroad.append(roadName)
                subcoordPaths.append(pathCoord)
                subtravelDuration.append(travelDurationTraffic)

            roads.append(subroad)
            coordPaths.append(subcoordPaths)
            travelDurations.append(subtravelDuration)

        return roads, coordPaths, travelDurations

    def closesttraveldurationfile(self):
        """Gives the name of the travel duration file corresponding to self.time

        :param path: string, indicate where is located the data
        :param time: string, self
        :return: string, file name
        """
        # TODO check that it actually works once some data has been retrieved
        files = os.listdir(self.pathTravelDuration)
        # retrieve files generated +/- 10mn from self.time
        file = [f for f in files if (int(split('_',f)[-1]) > (int(self.time)-10) and int(split('_',f)[-1]) < (int(self.time)+10))]

        return file[0]


    def reward(self, a):
        """
            Traveling time between lastAction and a

        :return: integer
        """
        # TODO read durations ! solve the problem of indexing: action should be indexed on self.customerState ? por self.tasks ?
        # return self.durations[self.lastAction][]
        pass
    
    def traveldurationdata(self, cluster):
        """Retrieve Bing API travel durations with traffic for all the instance's locations to visit

        :param cluster: name to identify locations covered
        :return: write a binary file containing the list of travel duration of all the links of the instances locations
                File format 'travelDuration_identifier_MM-DD_HHh_mm'
                Ex of list: OutputList[0][0] contains the travel duration between self.locations[0] and self.locations[1]
        """

        roads, coordPaths, travelDurations = self.infolinks()

        # write the binary files to retain this data !
        curpath = os.path.abspath(os.curdir)
        date = time.localtime()
        with open(curpath+'/travel_duration_data/travelDuration_'+cluster+'_'+str(date.tm_mon)+'-'+str(date.tm_mday)+'_'+\
                          time.strftime("%H%M"), 'wb') as fp:
            pickle.dump(travelDurations, fp)


if __name__ == "__main__":

        datapath = "/home/louis/Documents/Research/Code/foo-Environment_2/dynamics/demand_models/"
        curPath = os.path.abspath(os.curdir)

        # load delivery data
        deliverydata = np.loadtxt(datapath+"fedex.data")
        mask = deliverydata[:,0] == 2122015 # 2 dec 2015
        deliverydata = deliverydata[mask]

        deliverydata = deliverydata[123:157, :]  # 4th truck
        print(deliverydata.shape)

        # class instance
        instance1 = FooEnv(deliverydata)

        # Initialize
        instance1._reset()

        def job():
            # # Information about routing between each location
            # store in a binary file
            instance1.traveldurationdata("truck_4_2dec2015")
            print("One file written at "+time.strftime("%H%M"))
        # job()

        schedule.every(10).minutes.do(job)

        job()

        while True:  # TODO insert this loop in the traveldurationdata function so that the process can be reproduced
            try:
                # start = time.time()
                schedule.run_pending()
                # end = time.time()
                # print("Job done at "+time.strftime("%H%M"))
                # time.sleep(10*60 - (end - start) - 1*60)
            except:
                print("Route computation failure - Waiting before trying again")
                time.sleep(10)

        # # Retrieve travel durations from file
        # with open(curPath+'/travel_duration_data/travelDuration_4thTruck_2dec2015_2-13_15h_43', 'rb') as fp:
        #     itemlist = pickle.load(fp)
        #     print(itemlist)
