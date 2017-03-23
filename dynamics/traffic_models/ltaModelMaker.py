#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 13:25:31 2017

@author: Louis
"""
import time
import numpy as np
import os
import sys
# sys.path.append('/home/louis/Documents/Research/Code/foo-Environment_2/dynamics')  # add the path of gym-foo directory
import pickle
from dynamics.fooTools import *
from matplotlib import pyplot as plt


dataPath = '/media/louis/WIN10OS/Users/e0022825/Documents/Research/dataSpeedBandLTA'


def ltaRoads(files):
    """Return a tuple: [0] the set of roads for which we have speed data.
    The id of each road is its index.
    [1] nb of roads
    
    @Input: files, list of JSON file names containing the speed band data
    
    """
    ltaRoads = []
    for file in files:
        data = loadJSON(dataPath+'/'+file)
        for road in data:
            ltaRoads.append(road['RoadName'])
     
        ltaRoads = list(set(ltaRoads))
        
    ltaRoads.sort()
    
    return ltaRoads, len(ltaRoads)


def ltaRoadsSlot(file):
    """Return the set of roads for one JSON file, corresponding to one slot time.
    This is to check if there are less measured roads than the maximum number of roads
    measured during all our retrieving period.
    
    """
    data=loadJSON(dataPath+'/'+file)
    roads=[]
    for road in data:
        roads.append(road['RoadName'])
    roads=list(set(roads))
    
    roads.sort()
    return roads
    
""" TO BE STORED AND LOADED WHEN NEEDED ! """


def fileNameToInt(file):
    """Transform file name into an int. We assume the format in the example below.
    
    @Input: string, ex: speedBand00h00-26-01-2017
    @Output: int, ex: -> 201726010000 ie YYYYDDMMHHmm
    
    /!\ HOURS and MN in the end to include 00h00 as integers, Year at first
    """
    string=re.split('-',file)
    time=re.split('h',string[0][9:14])
    
    date=string[3][0:4]+string[1]+string[2]+time[0]+time[1]
    return int(date)


def speedJSONtoNp(files):
    """Return 2 np arrays, one for max speed and one for min speed
    
    @Input: files, list of name files to be examined (speed data)
    
    @Output: np arrays (max and min speed), nbFiles * (1+nbRoads) containing the speeds.
    The first column contains the time and date of the measure.

    set of all measured roads
    nb of measured roads
    """
    maxSpeed = []
    # minSpeed = []
    ltaroads, nbRoads = ltaRoads(files)  # set of all measured roads, nb of them

    for file in files:  # examining each 5mn
        print(file)
        data = loadJSON(dataPath+'/'+file)  # list of dictionary
        roads = ltaRoadsSlot(file)  # roads measured at this time slot
        rowM = []
        # rowm = []
        rowM.append(fileNameToInt(file))
        # rowm.append(fileNameToInt(file))
        for i in range(nbRoads):  # for each road (i is the ID)
                # print(data['value'][i]['RoadName'])
            if i < len(data):  # case where the current file carry info on the i road
                if (data[i]['RoadName'] in roads and data[i]['MaximumSpeed']):  # road actually measured
                    #  at this time slot
                    rowM.append(int(data[i]['SpeedBand']))
                else:
                    rowM.append(-1)  # no measure

                # if (data[i]['RoadName'] in roads and data[i]['MinimumSpeed']):  # road actually measured
                #     # at this time slot
                #     rowm.append(int(data[i]['MinimumSpeed']))
                # else:
                #     rowm.append(-1)  # no measure
            else:
                rowM.append(-1)  # no info
                # rowm.append(-1)  # no info
        maxSpeed.append(rowM)
        # minSpeed.append(rowm)
    maxSpeed  = np.asarray(maxSpeed)
    # minSpeed = np.asarray(minSpeed)
    return maxSpeed  # , minSpeed, ltaroads, nbRoads


def npArrayToTxt(speedData, name,fmt) :
    """Send numpy data array to a compressed txt file
    
    @Input
        speedData: np array 
        name: str, name of the output file (.gz is added)
        fmt: str or list of str, digits formatting ex: '%.3d'
    
    @Output
        compressed txt file
    """
    np.savetxt(name+'.gz' , speedData, fmt=fmt)
    
    
if __name__ == "__main__":

    # # list of files to be treated: give JSON file names only, not the path
    # path_to_json = '/media/louis/WIN10OS/Users/e0022825/Documents/Research/dataSpeedBandLTA'
    # files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    #
    # # load JSON and generate a np array
    # band = speedJSONtoNp(files)
    # print(band.shape)  # 1742,4074?
    #
    # # save the array into a text file
    # fmt = "%.3d"
    # npArrayToTxt(band,'Band_'+files[0][:-5]+'_'+files[-1][:-5],fmt)
    # # npArrayToTxt(minSpeed, 'minSpeedBand_09h20-25-01-2017_to_10h30-31-01-2017', fmt)

    # data
    Band = np.loadtxt('/home/louis/Documents/Research/Code/foo-Environment_2/dynamics/traffic_models/'
                           'Band_speedBand09h15-26-01-2017_speedBand17h45-26-01-2017.gz', dtype=int)

    for routenb in range(4,5):
        starttime = 7 # o'clock
        timespan = 12 # hours
        roads = []

        # Road names load the file
        with open('addresses.lta','rb') as fp:
            ltaroads = pickle.load(fp)
            road = ltaroads[routenb - 1]  # road name
            print(road)

        plt.scatter(range(timespan * 12), Band[(starttime * 12):(timespan * 12 + starttime * 12), routenb], label=road)
        plt.legend()

    plt.show()

    