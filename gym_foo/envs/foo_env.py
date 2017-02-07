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
        # FedEx data
        self.locations = deliverydata[:,4]  # Addresses ID

        # Delivery locations to visit
        mask_d = self.locations[:,7] == 'N/A'
        self.deliveryLocations = self.locations[mask_d]  # ID of the delivery locations, Coordinates
        self.ndl = np.size(self.locations[mask_d])

        # Pick-up locations to visit : invisible to the agent (pre-loaded scenario)
        mask_p = self.locations[:,7] != 'N/A'
        self._pickupLocations = self.locations[mask_p]  # ID of the pickup addresses
        self._ndp = np.size(self.locations[mask_p])

        # Tasks ahead
        mask_ta = self.deliverydata[:,7] != 'N/A'
        self.tasksAhead = self.deliverydata[mask_ta]

        # Time related variables
        # Duration of one time step in mn
        self.timeStep = 30

        # Start of operations
        self.startTime = '0800'  # 8am

        # Number of ways to classify congestion traffic on one arc
        # ex: nC=2 => traffic on one arc classified as non-jammed (0) or jammed (1)
        self.nC = 2

        # Define the state, see _reset() for a meaningful initialization
        self.time = 0
        self.currentLocation = 0
        self.congestionStatus = 0
        self.customerState = 0

        self.s = self.time, self.currentLocation, self.congestionStatus, self.customerState

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
        mask_t = self.deliverydata[:, 7] == 'N/A'
        self.tasks = self.deliverydata[mask_t]

        self.time = self.startTime
        self.currentLocation = self.deliveryLocations[0]  # First Address: depot
        self.congestionStatus = np.zeros(self.ndl,self.ndl)  # No congestion at first
        self.customerState = self.ndl * [0]  # No customer serviced yet,
        #  only deliveries are known at the beginning. this object gives ID to the jobs to be done

        return self.s

    def _step(self, a):
        """
            Give the next state and reward

        :param: a, action. ID of the location to visit, based on self.customerState
        :return: state, reward, done or not, info
        """
        if (a < self.tasks.shape[0] & !(self.done)):
            # STATE
            # Increase time
            self.time += self.timeStep

            # Update locations to visit: new demand maybe !
            # Update current tasks
            mask_update = self.time > self.tasksAhead[:, 7]
            newTasks = self.tasksAhead[mask_update]
            self.tasks = np.concatenate((self.tasks, newTasks), axis=0)  # Add the new jobs

            # Congestion Status
            self.congestionStatus = self.congestionupdate()

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

    def congestionupdate(self):
        """
            Update congestion status
        :return: np.zeros(self.ndl + self.ndp, self.ndl + self.ndp)
        """
        # TODO Implement the function that gives the congestion status (integer) of every routes linking our tasks.
        # TODO using data or API ? Probably data
        pass

    def reward(self, a):
        """
            Traveling time between lastAction and a

        :return: integer
        """
        # TODO estimate traveling time between the locations using fooTools !
        pass