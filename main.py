#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 13:41:00 2017

@author: Louis
"""
import sys
sys.path.append('/home/louis/Documents/Research/Code/foo-Environment_2/dynamics') # add the path of gym-foo directory

print(sys.path)

from dynamics.fooTools import *
import schedule
import time
import os


if __name__ == "__main__":
    
    # list of files to be treated
    files = os.listdir('/media/louis/WIN10OS/Users/e0022825/Documents/Research/dataSpeedBandLTA')


    # load JSON and generate a np array
    maxSpeed, minSpeed = speedJSONtoNp(files[0:2])

    # save the array into a text file
    npArrayToTxt(maxSpeed, 'speedBand_test')