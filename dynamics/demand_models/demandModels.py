#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 15:38:50 2017

@author: Louis
"""

import time
from sklearn.neighbors import KernelDensity
import csv

# import json, requests
import numpy as np

import re # string splitting

# Ubuntu fedex.data path
fedex_data_path = "/home/louis/Documents/Research/Code/foo-Environment_2/dynamics/demand_models/"

def demandRetriever():
    """
    Put the whole demand into a single array with features given below.
        
    
    Days to examine:
        cleaned01-Dec-2015
        cleaned02-Dec-2015
        cleaned03-Dec-2015
        cleaned04-Dec-2015
        cleaned07-Dec-2015
        cleaned08-Dec-2015
        cleaned09-Dec-2015
        cleaned10-Dec-2015
        cleaned11-Dec-2015
        cleaned14-Dec-2015
        cleaned15-Dec-2015
        cleaned16-Dec-2015
        cleaned17-Dec-2015
        cleaned18-Dec-2015
        cleaned21-Dec-2015
    
    @output:  measures: array [n_samples, n_features]
                        
                        Features are: day (int from 1 to 5, no week-end)
                                        Longitude   (float) 
                                            Latitude  (float)
                                                ReadyTime (int)
                                                    CloseTime  (int)
                            
                    
    The delimiter in the csv file is set to ','
    The input csv file must have a column called 'Address' and 'FedEx ID'
    """
    
    #Strings to load data
    stringFile='/Users/Louis/Documents/Research/Code/cleanedData/'
    days={'cleaned01-Dec-2015':2,#tuesday
        'cleaned02-Dec-2015':3,#wednesday
        'cleaned03-Dec-2015':4,#...
        'cleaned04-Dec-2015':5,
        'cleaned07-Dec-2015':1,
        'cleaned08-Dec-2015':2,
        'cleaned09-Dec-2015':3,
        'cleaned10-Dec-2015':4,
        'cleaned11-Dec-2015':5,
        'cleaned14-Dec-2015':1,
        'cleaned15-Dec-2015':2,
        'cleaned16-Dec-2015':3,
        'cleaned17-Dec-2015':4,
        'cleaned18-Dec-2015':5,
        'cleaned21-Dec-2015':1}
        
    #Store results
    measures=[]
     
    for day in days.keys():
        #Configuration for CSV reading
        with open(stringFile+day+'_modified.csv') as csvfile:
            #Dictionary containing the info
            reader=csv.DictReader(csvfile,delimiter=',')
            #print(day)
            
            for row in reader:
                if row['ReadyTimePickup']!='N/A' and row['Longitude']!='N/A':#pick-up
                    measures.append([days[day],float(row['Longitude']),float(row['Latitude']),
                                     int(row['ReadyTimePickup']),int(row['CloseTimePickup'])])
            
    measures=np.asarray(measures)
                
    return measures
    
#measures=demandRetriever()
#print(measures.shape)



# Let's create a Kernel Density Estimation for one specific day, at one time
#Monday, between 1000 and 1030
def modelGenerator(data,day,startTime,timeSpan):
    """
    
    @Input
        data: np.array, containing encoded data of demand (result of demandRetriever function)
        day: str, day of the week NO CAPITAL LETTER
        startTime: int, starting time of the time slot (1030 => 10h30mn)
        timeSpan: int, length in mn of the time slot
            /!\ Add geographic boundaries later ? /!\
            /?\ Options in KernelDensity : gaussian kernel, bandwidth etc.  /?\ 
        
    @Output
        KernelDensity object representing the demand probability distribution
        at the time corresponding to the inputs.
            
    
    """
    days={'monday':1,'tuesday':2,'wednesday':3,'thursday':4,'friday':5,'saturday':6}
    mask=(data[:,0]==days[day]) & (data[:,3]>startTime) & (data[:,3]<startTime+timeSpan)
    print(data[mask].shape)

    #Corresponding KernelDensity model: Parameters to be reviewed !!
    kde = KernelDensity(bandwidth=0.04,
                        kernel='gaussian', algorithm='ball_tree')
    kde.fit(data[mask][:,1:3])#remove unnecessary features (day, times)

    return kde


# VERSION 2 for fedex.data file (very smilar to the previous one
def modelGenerator_fedex_data(data, day, startTime, timeSpan):
    """

    @Input
        data: np.array, fedex.data (complete data)
        day: str, day of the week NO CAPITAL LETTER
        startTime: int, starting time of the time slot (1030 => 10h30mn)
        timeSpan: int, length in mn of the time slot
            /!\ Add geographic boundaries later ? /!\
            /?\ Options in KernelDensity : gaussian kernel, bandwidth etc.  /?\

    @Output
        KernelDensity object representing the demand probability distribution
        at the time corresponding to the inputs.


    """
    start = time.time()
    days = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6}
    mask = (data[:, 1] == int(days[day])) & (data[:, 7] > startTime) & (data[:, 7] < startTime + timeSpan)
    print(data[mask].shape)

    # Corresponding KernelDensity model: Parameters to be reviewed !!
    kde = KernelDensity(bandwidth=0.04,
                        kernel='gaussian', algorithm='ball_tree')
    kde.fit(data[mask][:, -2:])  # meaningful features: Longitudes and Latitudes
    end = time.time()
    print(end - start)
    return kde
    
#kde.sample(3) #sample 3 coordinates
  

#------------------------------------------------------------------------------
#           Formating data
# 
#------------------------------------------------------------------------------
 
def formatDate(string):
    """Give an integer as a date. DDMMYY
    
    """
    splitStr=re.split('-',string)
    return int(splitStr[0]+'12'+splitStr[2])
    
def formatAddress():
    """Retrieve all the visited addresses and return a set of it, sorted by alphabetical order
    
    """
    #Strings to load data
    stringFile='/media/louis/WIN10OS/Users/e0022825/Documents/Research/data_fedex'
    days={'cleaned01-Dec-2015':2,#tuesday
        'cleaned02-Dec-2015':3,#wednesday
        'cleaned03-Dec-2015':4,#...
        'cleaned04-Dec-2015':5,
        'cleaned07-Dec-2015':1,
        'cleaned08-Dec-2015':2,
        'cleaned09-Dec-2015':3,
        'cleaned10-Dec-2015':4,
        'cleaned11-Dec-2015':5,
        'cleaned14-Dec-2015':1,
        'cleaned15-Dec-2015':2,
        'cleaned16-Dec-2015':3,
        'cleaned17-Dec-2015':4,
        'cleaned18-Dec-2015':5,
        'cleaned21-Dec-2015':1}
        
    #Store results
    addresses=[]
    CourierSuppliedAddresses=[]
     
    for day in days.keys():
        #Configuration for CSV reading
        with open(stringFile+day+'_modified.csv') as csvfile:
            #Dictionary containing the info
            reader=csv.DictReader(csvfile,delimiter=',')
            #print(day)
            
            for row in reader:
                addresses.append(row['Address'])
                CourierSuppliedAddresses.append(row['CourierSuppliedAddress'])
                
    addresses=list(set(addresses))
    addresses.sort()
    
    CourierSuppliedAddresses=list(set(CourierSuppliedAddresses))
    CourierSuppliedAddresses.sort()
    return addresses, CourierSuppliedAddresses
    
    
    
def formatPickup(string):
    """Return an int when it's not 'N/A' and O otherwise
    
    """
    if string=='N/A':
        return 0
    else:
        return int(string)
        
def formatCoordinates(string):
    """Return a float when it's not 'N/A' and O otherwise
    
    """
    if string=='N/A':
        return 0
    else:
        return float(string)
        
def formatPostalCode(string):
    """Return the corresponding int when the format is correct, 0 otherwise
    
    """
    if string.isdigit():
        return int(string)
    else :
        return 0
    
        
def formatPickupType(string):
    """Encode the pickup type with an int
    
    0:N/A, 1:D, 2:M, 3:C, R:4, T:5
    """
    if string == 'N/A':
        return 0
    elif string == 'D':
        return 1
    elif string == 'M':
        return 2
        
    elif string == 'C':
        return 3
        
    elif string == 'R':
        return 4
        
    else:
        return 5
        
    
def dataToNumpy():
    """Send all our data into a numpy array, which features are described after
    
    @Output: numpy array which features are:
    ['StopDate','WeekDay','StopOrder','StopStartTime','Address','PostalCode',
        'CourierSuppliedAddress','ReadyTimePickup','CloseTimePickup','PickupType',
        'WrongDayLateCount','RightDayLateCount','FedExID','Longitude','Latitude']

    This has been stored once for all as fedex.data !    
    
    """
    
    #Strings to load data
    stringFile='/Users/Louis/Documents/Research/Code/cleanedData/'
    days={'cleaned01-Dec-2015':2,#tuesday
        'cleaned02-Dec-2015':3,#wednesday
        'cleaned03-Dec-2015':4,#...
        'cleaned04-Dec-2015':5,
        'cleaned07-Dec-2015':1,
        'cleaned08-Dec-2015':2,
        'cleaned09-Dec-2015':3,
        'cleaned10-Dec-2015':4,
        'cleaned11-Dec-2015':5,
        'cleaned14-Dec-2015':1,
        'cleaned15-Dec-2015':2,
        'cleaned16-Dec-2015':3,
        'cleaned17-Dec-2015':4,
        'cleaned18-Dec-2015':5,
        'cleaned21-Dec-2015':1}
     
    #All the addresses
    addresses,CourierSuppliedAddresses=formatAddress()

     
    #Store results
    measures=[]
     
    for day in days.keys():
        #Configuration for CSV reading
        with open(stringFile+day+'_modified.csv') as csvfile:
            #Dictionary containing the info
            reader=csv.DictReader(csvfile,delimiter=',')
            #print(day)
            
            for row in reader:
                measures.append([formatDate(row['StopDate']),
                                           days[day],
                                           int(row['StopOrder']),
                                           int(row['StopStartTime']),
                                           addresses.index(row['Address']),
                                           formatPostalCode(row['PostalCode']),
                                           CourierSuppliedAddresses.index(row['CourierSuppliedAddress']),
                                            formatPickup(row['ReadyTimePickup']),
                                            formatPickup(row['CloseTimePickup']),
                                            formatPickupType(row['PickupType']),
                                            formatPickup(row['WrongDayLateCount']),
                                            formatPickup(row['RightDayLateCount']),
                                            int(row['FedExID']),
                                            formatCoordinates(row['Longitude']),
                                            formatCoordinates(row['Latitude'])]
                                     )
    #/!\ MODIF ??? 
                        
    measures=np.asarray(measures)
    return measures
    
#start=time.time()  
#measures=dataToNumpy()
#print(measures.shape)
#end=time.time()  
#print("Generating time before storing: %d" % (end-start))    
   

def numpyToTxt(measures,name):
    """Store a numpry array into a txt file
    
    @Input
        measures: numpy array
        name: string, name of the output file
        
    @Output
        txt file
    
    """
    header="StopDate,WeekDay,StopOrder,StopStartTime,Address,PostalCode,\
        CourierSuppliedAddress,ReadyTimePickup,CloseTimePickup,PickupType,\
        WrongDayLateCount,RightDayLateCount,FedExID,Longitude,Latitude"
    
    np.savetxt('fedex.data',measures, fmt=['%.8d', '%.2d', '%.2d', '%.4d', '%.6d', '%.4d', '%.4d', '%.4d', '%.4d', '%.4d', '%.4d', '%.4d', '%.4d', '%.18f', '%.18f'], header=header)
  
    
 # Function to rename headers of our .csv.......   
def csvHeader():
    
    days={'cleaned01-Dec-2015':2,#tuesday
        'cleaned02-Dec-2015':3,#wednesday
        'cleaned03-Dec-2015':4,#...
        'cleaned04-Dec-2015':5,
        'cleaned07-Dec-2015':1,
        'cleaned08-Dec-2015':2,
        'cleaned09-Dec-2015':3,
        'cleaned10-Dec-2015':4,
        'cleaned11-Dec-2015':5,
        'cleaned14-Dec-2015':1,
        'cleaned15-Dec-2015':2,
        'cleaned16-Dec-2015':3,
        'cleaned17-Dec-2015':4,
        'cleaned18-Dec-2015':5,
        'cleaned21-Dec-2015':1}
        
    for inputFileName in days.keys():
        outputFileName = '/Users/Louis/Documents/Research/Code/cleanedData/'+inputFileName + "_modified.csv"
        inputFileName='/Users/Louis/Documents/Research/Code/cleanedData/'+inputFileName+'.csv'
        with open(inputFileName, newline='') as inFile, open(outputFileName, 'w', newline='') as outfile:
            r = csv.reader(inFile)
            w = csv.writer(outfile)

            next(r, None)  # skip the first row from the reader, the old header
            # write new header
            w.writerow(['StopDate','StopOrder','StopStartTime','Address','PostalCode','CourierSuppliedAddress','ReadyTimePickup','CloseTimePickup','PickupType','WrongDayLateCount','RightDayLateCount','FedExID','Longitude','Latitude'])

            # copy the rest
            for row in r:
                w.writerow(row)
                
