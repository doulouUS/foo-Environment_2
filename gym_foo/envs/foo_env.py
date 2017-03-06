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
from datetime import date, datetime, timedelta
from datetime import time as t

import csv
import os
import schedule
from re import split

def timeupdate(string, timestep):
    """

    :param string 'HHmm', timestep integer in minutes
    :return: string updated 'HHmm'
    """
    update = datetime.combine(date.today(), t(int(string[0:2]), int(string[2:4]))) + timedelta(minutes=timestep)

    if update.hour < 10:
        if update.minute < 10:
            return '0' + str(update.hour) + '0' + str(update.minute)
        else:
            return '0' + str(update.hour) + str(update.minute)
    else:
        if update.minute < 10:
            return str(update.hour) + '0' + str(update.minute)
        else:
            return str(update.hour) + str(update.minute)

class FooEnv(gym.Env):

    metadata = {'render.modes': ['human']}

    def __init__(self, deliverydata, startTime='0800' ):
        """


        :param deliverydata: np array     ['StopDate','WeekDay','StopOrder','StopStartTime','Address','PostalCode',
            'CourierSuppliedAddress','ReadyTimePickup','CloseTimePickup','PickupType',
            'WrongDayLateCount','RightDayLateCount','FedExID','Longitude','Latitude']

            /!\ Make sure the first line of this array is the depot /!\

            startTime: string, 'HHMM'

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

        # Duration of servicing time in mn
        self.serving_time = 6.5

        # Start of operations
        self.startTime = startTime

        # STATE RELATED
        # Number of ways to classify congestion traffic on one arc
        # ex: nC=2 => traffic on one arc classified as non-jammed (0) or jammed (1)
        self.nC = 2

        # Define the state, see _reset() for a meaningful initialization
        self.time = "0"
        self.currentLocation = 0
        self.durations = []

        self.tasks = np.zeros((1,1))  # dumb initialization
        self.visited_customer = [0] * self.tasks.shape[0]  # customer visited (1) and not visited (0) indexed on self.tasks

        self.s = self.time, self.currentLocation, self.durations, self.visited_customer

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
        self.tasks = self.deliverydata[self.mask_d]  # at first only deliveries are known
        self._tasksAhead = self.deliverydata[self.mask_p]  # pickups to be done in the scenario: invisible to agent

        self.time = self.startTime
        self.currentLocation = self.deliveryLocations[0]  # First Address: depot
        try:
            # Read file corresponding to the current time (here self.starttime)
            self.traveltimereader()
        except:
            print("WARNING: Setting durations to an empty list because error on travel duration retrieval (init)")
            self.durations = []

        self.visited_customer = [1] + [0] * (self.tasks.shape[0] - 1)  # starting from the first task,
        #  it has been visited => 1

        print("Initialization done.")

        return self.s

    def _step(self, a):
        """
            Give the next state and reward

        :param: a, action. index of the location in self.tasks (containing all the possible locations at time self.time
        :return: state, reward, done or not, info
        """
        if a < self.tasks[:, 3].size:

            if int(self.time) > 1150 and int(self.time) < 1330:  # lunch break at 1145pm # TODO test extensively this !!
                self.time = '1400'  # only time has changed, but the state remains the same
                reward = 2 * 3600  # 2 hours in s
                info = "Lunch break"
                return self.s, reward, self.done, info

            else:

                # STATE
                # Increase time by traveling time (i.e reward) and servicing time and round to have a result
                #  in mn (compatible with our strings
                # TODO increase self.time by the reward is not flexible for what comes next: better replace it by traveling times directly
                self.time = timeupdate(self.time, int(np.round(self.reward(a) / 60 + self.serving_time)))

                # REWARD: traveling time from lastAction to a (or depot to a if starting)
                reward = self.reward(a)

                # Update locations to visit: new demand maybe !
                # Update current tasks
                mask_update = int(self.time) > self._tasksAhead[:, 7]
                newTasks = self._tasksAhead[mask_update]
                # Among tasks in newTasks, pick the one that are not already in self.tasks
                # TODO this does not seem to work
                newTasks = [row for row in newTasks if np.array_equal(np.all(self.tasks == row, axis = 1),\
                                                                      np.zeros( self.tasks.shape[0], dtype=bool))]

                print("NB of NEW TASKSS", len(newTasks))
                if len(newTasks) != 0:
                    print("New pickup requested")

                    # sort the new tasks by chronological order of appearance
                    newTasks = np.array(newTasks)
                    newTasks = newTasks[np.argsort(newTasks[:, 7])]

                    self.tasks = np.concatenate((self.tasks, newTasks), axis=0)  # Add the new jobs
                    self.visited_customer.extend(len(newTasks) *[0])  # Add new jobs to be done

                # Congestion Status
                try:
                    # Read file corresponding to the current time
                    self.traveltimereader()
                except:
                    print("WARNING: Setting durations to an empty list because error on travel duration retrieval")
                    self.durations = []

                # Update customerState, if not the first move
                print("list of tasks size ", self.visited_customer)
                self.visited_customer[a] += 1

                # Current location
                self.currentLocation = self.tasks[a, 4]  # Address

                self.lastAction = a

                # END STATUS
                if (len(self.visited_customer) == (self.ndl + self._npl)):
                    self.done = True

                # INFO
                info = "A useful info please"

                return self.s, reward, self.done, info

        else:
            print("Action not available or End of operations")
            return [0]*4


    def _render(self, mode='human', close=False):
        """For now, return human readable information to follow van progress

        :param mode:
        :param close:
        :return:
        """
        # TODO If time permits, display a more meaningful congestion status (colored graph depending on travel duration)
        # Retrieve string addresses of locations to visit
        with open('/home/louis/Documents/Research/Code/foo-Environment_2/gym_foo/envs/addresses.fedex', 'rb') as fp:
            addresses = pickle.load(fp)

        print("-" * 33 + '|' + "-" * 35)
        print("Current time: (before servicing) | ", self.time)
        print("-" * 33 + '|' + "-" * 35)
        print("Current Location: (to be served) | " + addresses[int(self.currentLocation)])
        print("-" * 33 + '|' + "-" * 35)
        print("Congestion Status:               | to be DONE ....")
        print("-" * 33 + '|' + "-" * 35)

        return 0

    def infolinks(self):
        """Gives info about all the links between the locations to visit
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

        for idxStart in range(self.locations.size - 1):  # TODO this -1 is certainly WRONG !
            subroad = [] # contains all the roads starting from idxStart
            subcoordPaths = []
            subtravelDuration = []

            for idxEnd in range(idxStart + 1, self.locations.size):
                # Retrieve string addresses of locations to visit

                location1 = self.addressretriever(self.locations[idxStart])
                location2 = self.addressretriever(self.locations[idxEnd])
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

        files = os.listdir(self.pathTravelDuration)
        # retrieve files generated +/- 8mn from self.time: can BE MODIFIED if enough data !

        upTime = datetime.combine(date.today(), t(int(self.time[0:2]), int(self.time[2:4])))\
                 + timedelta(minutes=10)

        downTime = datetime.combine(date.today(), t(int(self.time[0:2]), int(self.time[2:4])))\
                 - timedelta(minutes=10)

        file = [f for f in files if t(int(split('_', f)[-1][0:2]), int(split('_', f)[-1][2:4])) < upTime.time() and t(int(split('_',f)[-1][0:2]), int(split('_',f)[-1][2:4])) > downTime.time() ]
        print("Travel duration file used: ", file[0])
        return file

    def addressretriever(self, id):
        """

        :param id: integer or np.float (but that can be converted to an int), id of the address
        :return: string, human readable address
        """
        with open('/home/louis/Documents/Research/Code/foo-Environment_2/gym_foo/envs/addresses.fedex', 'rb') as fp:
            addresses = pickle.load(fp)

        return addresses[int(id)]

    def traveltimereader(self):
        """

        :param a: integer, index of the starting point
        :param b: integer, index of the ending point
        :param time: string giving the desired time when we need the travel time ('HHMM')
        :return: integer, nb of seconds
        """
        files = os.listdir(self.pathTravelDuration)
        # retrieve files generated +/- 8mn from self.time: can BE MODIFIED if enough data !


        file = [f for f in files if
                (int(split('_', f)[-1]) > (int(self.time) - 8) and int(split('_', f)[-1]) < (int(self.time) + 8))]




        with open(self.pathTravelDuration + self.closesttraveldurationfile()[0], 'rb') as fp:
            print()
            self.durations = pickle.load(fp)
        return self.durations


    def reward(self, a):
        """
            Traveling time between lastAction and a

        :return: integer, nb of seconds
        """
        # TODO test it: pb when no travel time haas been retrieved (durations -> 0 )
        # print(self.lastAction)
        try:
            if self.lastAction != -1:
                if self.lastAction < a:
                   return self.durations[self.lastAction][a - self.lastAction -1]
                else:
                   return self.durations[a][self.lastAction - a -1]  # list of list built as a triangular matrix...

            else:
                return self.durations[0][a-1]  # First move always start from self.tasks[0, :]


        except:
            print("Error in the reward function: assigned a duration at random....")
            return 1000


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
