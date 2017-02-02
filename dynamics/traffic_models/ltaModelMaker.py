# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 13:25:31 2017

@author: Louis
"""

from fooTools import *
import numpy as np

dataPath='/anaconda/lib/python3.5/site-packages/gym-foo/dynamics'

fileName='speedBand00h00-26-01-2017'
files=[fileName] #will contain all the files to be searched

data=loadJSON(dataPath+'/'+fileName+'.json')

print(data['value'][0].keys())

def ltaRoads(files):
    """Return a tuple: [0] the set of roads for which we have speed data.
    The index of each road is its index.
    [1] nb of roads
    
    @Input: files, list of JSON files containing the speed band data
    
    """
    ltaRoads=[]
    for file in files:
        data=loadJSON(dataPath+'/'+file+'.json')
        for road in data['value']:
            ltaRoads.append(road['RoadName'])
     
        ltaRoads=list(set(ltaRoads))
        
    ltaRoads.sort()
    
    return ltaRoads, len(ltaRoads)
    
def ltaRoadsSlot(file):
    """Return the set of roads for one JSON file, corresponding to one slot time.
    This is to check if there are less measured roads than the total number of roads
    given by ltaRoads.
    
    """
    data=loadJSON(dataPath+'/'+file+'.json')
    roads=[]
    for road in data['value']:
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

def SpeedData(files):
    """Return a np array
    
    @Input: files, list of name files to be examined
    
    @Output: np array, nbFiles * (1+nbRoads) containing the max speed.
    The first column contains the date of the measure.
    """
    maxSpeed=[]
    minSpeed=[]
    ltaroads,nbRoads=ltaRoads(files)#set of all measured roads, nb of them
    #print(ltaRoads)
    for file in files:#examinibg each 5mn
        data=loadJSON(dataPath+'/'+file+'.json')#dictionary
        roads=ltaRoadsSlot(file)#roads measured at this time slot
        rowM=[] 
        rowm=[]
        rowM.append(fileNameToInt(file))
        rowm.append(fileNameToInt(file))
        for i in range(nbRoads):#for each road (i is the ID)
            #print(data['value'][i]['RoadName'])
    
            if (data['value'][i]['RoadName'] in roads and data['value'][i]['MaximumSpeed']): #road actually measured at this time slot             
                rowM.append(int(data['value'][i]['MaximumSpeed']))
            else:
                rowM.append(-1) #no measure
                
            if (data['value'][i]['RoadName'] in roads and data['value'][i]['MinimumSpeed']): #road actually measured at this time slot             
                rowm.append(int(data['value'][i]['MinimumSpeed']))
            else:
                rowm.append(-1) #no measure
        maxSpeed.append(rowM)
        minSpeed.append(rowm)
    maxSpeed=np.asarray(maxSpeed)
    minSpeed=np.asarray(minSpeed)
    return maxSpeed, minSpeed
maxSpeed,minSpeed=SpeedData(files)
mask=maxSpeed[0,:]==-1
mask2=minSpeed[0,:]==0
print(maxSpeed[mask].shape,minSpeed[mask2].shape)
print(maxSpeed>minSpeed)
        

    
    


        
    