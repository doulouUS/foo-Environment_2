#!/usr/bin/python3.5
#  -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 09:39:45 2017

@author: Louis
"""
import requests
import json
import csv
# import urllib.parse
# from urllib.parse import urlparse

import re

from tempfile import TemporaryFile # store the data as a numpy array

# import httplib2 as http # External library

# Useful help
#  https://github.com/hiimivantang/ltadatamallcrawler

# ------------------------------------------------------------------------------
#                        APIs
# ------------------------------------------------------------------------------
#  LTA
AccountKey = "8Q6acuQNTAGl8r/GqViFtA =  = "
UniqueUserID = '8ecabd56-08a2-e843-0a7a-9944dccf124a'
#  Headers
headers  =  {
    'AccountKey': AccountKey,
    'UniqueUserID': UniqueUserID,
    'accept': 'application/json'
}

#  Bing
API_Key = "Avah46_M-gfFeQ3P1w09Qq1ElAV9ZEHFDm9b8JRCRa8qPP5uVn21hDqAPVJgV4i_"

#  ------------------------------------------------------------------------------
#                        Deliveries related
#  ------------------------------------------------------------------------------

def jobsAsDict (string, nbTrucks):
    """Retrieve sequences of customers to visit and the pick-ups occuring
    when operating.
    
    @Input
    string: file's name of the day to process ex: cleaned01-Dec-2015.csv 
    (added to /Users/Louis/Documents/Research/Code/cleanedData/ to create a valid path)
    
    nbTrucks: nb of sequence to retrieve
    
    @Ouput
    dicionary {'cluster_n':{'delivery_m':[Address,Longitude,Latitude]
                                
                                'pickUp_l':[Address,Longitude,Latitude,ReadyTimePickup,CloseTimePickup]}}
    """
    
    dictio = {'date': string[7:18]}    
    
    # Configuration for CSV reading
    with open('/Users/Louis/Documents/Research/Code/cleanedData/'+string) as csvfile:
        # Dictionary containing the info
        reader = csv.DictReader(csvfile,delimiter = ',')
        
        #  Keep track of numbers
        clusterNb = 0 #  sequences
        deliveryNb = 1 
        pickUpNb = 1
        
        dictSeq = {'Init' : [None,None,None]}
        
        for row in reader:
            
            if row['StopOrder'] == '1' : #  start of a new sequence
                
                
                dictio['cluster_'+str(clusterNb)] =  dictSeq.copy()
                clusterNb += 1
                if clusterNb == nbTrucks+1:
                    break
                #  Initialization

                dictSeq.clear()
                deliveryNb = 1
                pickUpNb = 1 
        
                if row['ReadyTimePickup'] == 'N/A': #  type: delivery
                
                    dictSeq['delivery_'+str(deliveryNb)] =  [row['Address'],\
                    row['Longitude'],row['Latitude']]
                    deliveryNb += 1
                else:
            
                    dictSeq['pickUp_'+str(pickUpNb)] =  [row['Address'],\
                    row['Longitude'],row['Latitude'],row['ReadyTimePickup'],row['CloseTimePickup']]
                    pickUpNb += 1
            else:
                
                if row['ReadyTimePickup'] == 'N/A': #  type: delivery
                
                    dictSeq['delivery_'+str(deliveryNb)] =  [row['Address'],\
                    row['Longitude'],row['Latitude']]
                    deliveryNb += 1
                else:
                    
                    dictSeq['pickUp_'+str(pickUpNb)] =  [row['Address'],\
                    row['Longitude'],row['Latitude'],row['ReadyTimePickup'],row['CloseTimePickup']]
                    pickUpNb  += 1

                                    
    return dictio   

def jobsToCSV(result,name,clusterNb = 1):
    """Send jobAsDict results into a csv file
    
    @Input
    result: dictionary, obtained by the jobsAsDict function
    name: string to name the output csv file (do not add .csv)
    clusterNb: choose which cluster to write down (default 1)
    
    @Output
    csv file with following header
    Address   Longitude   Latitude   Type   ReadyTime   EndTime
    
    """
    with open(name+'.csv', 'w') as f:  #  Just use 'w' mode in 3.x
        w  =  csv.DictWriter(f, ['Address','Longitude','Latitude','Type','ReadyTime','EndTime'])
        w.writeheader()
        for loc in result['cluster_'+str(clusterNb)].items():
            if loc[1][1] != 'N/A':#  make sure we have the coordinates
                
                if loc[0][0] == 'p': # pick-up
                    w.writerow({'Address':loc[1][0],'Longitude':loc[1][1],\
                    'Latitude':loc[1][2],'Type':'p','ReadyTime':loc[1][3],'EndTime':loc[1][4]})
                else:# delivery
                    w.writerow({'Address':loc[1][0],'Longitude':loc[1][1],\
                    'Latitude':loc[1][2],'Type':'d','ReadyTime':'None','EndTime':'None'})

# for i in range(11):
#     jobsToCSV(result,"01Dec-nb"+str(i),i)
# print(result['cluster_2']['delivery_1'])
# print(result['cluster_1']['delivery_1'])
# print(result['cluster_0']['Init'])

# ------------------------------------------------------------------------------
#                        Routing related
# ------------------------------------------------------------------------------
    
def roadSegments(locations):
    """Given 2 locations, return all the road segments joinning 
    these locations.
    
    Problem: limitations of the API (Bing, Google...)
    
    @Input
    locations: list for now, ?dictionnary-like ex: {clutser_1 :{'delivery_1' :[Address, Longitude, Latitude],
                                                'delivery_2' : [Address, Longitude, Latitude]}}
    
    @Output (tuples)
    statusCode  travelDistance   travelDuration   travelDurationTraffic (with traffic,
    not too sure about it)   numberSegments    itineraryItems
    """ 
    
    #  Base URL
    uri  =  'http://dev.virtualearth.net/' # Resource URL 
    path  =  'REST/v1/Routes?'
    
    
    #  URL Parameters
    params  =  { 'wayPoint.0' : locations[0]+',Singapore',
               'wayPoint.1' : locations[1]+',Singapore',
                'routeAttributes':'routePath',
                'key' : API_Key}                #  by default 'optimize' : 'time'} # this is by default
    
    url = uri+path

    results =  requests.get(
            url,
            params = params
        ).json()# ['resourceSets']

    #  Retrieving values
    statusCode = results['statusCode']
    if statusCode == 200:
        print(statusCode)
        travelDistance = results['resourceSets'][0]['resources'][0]['travelDistance']
        travelDuration = results['resourceSets'][0]['resources'][0]['travelDuration']
        travelDurationTraffic = results['resourceSets'][0]['resources'][0]['travelDurationTraffic']
        numberSegments = len(results['resourceSets'][0]['resources'][0]['routeLegs'][0]\
                        ['itineraryItems'])
        itineraryItems = results['resourceSets'][0]['resources'][0]['routeLegs'][0]\
                        ['itineraryItems']
        pathCoord = results['resourceSets'][0]['resources'][0]['routePath']['line']['coordinates']
        roadName = []
        travelDistances = []
        travelDurations = []
        maneuverType = []

        for seg in itineraryItems:
            for i in range(len(seg['details'])):
                print(i)
                roadName.append(seg['details'][i]['names'])
                travelDistances.append(seg['travelDistance'])
                travelDuration.append(seg['travelDuration'])
                maneuverType.append(seg['details'][i]['maneuverType'])

        return statusCode,travelDistance,travelDuration,travelDurationTraffic,numberSegments,roadName, \
               travelDistances, travelDurations, maneuverType, pathCoord

    else:
        print("Unsuccessful route calculation.")


# itinItems = roadSegments(['Redmond, WA','Issaquah, WA'])[5]
#  Interesting values to retrieve

#  Length browsed on this particular road
# print(resp['resourceSets'][0]['resources'][0]['routeLegs'][0]['itineraryItems']\
#                    [0]['travelDistance'])
#  Duration of traveling on this segment (CAN BE REFINED USING TRAFFIC CONSIDERATIONS)
# print(resp['resourceSets'][0]['resources'][0]['routeLegs'][0]['itineraryItems']\
#                    [0]['travelDuration'])
   
   

# ------------------------------------------------------------------------------
#                        LTA Data related
# ------------------------------------------------------------------------------      

def fetch_all_lta(url):
    """Retrieve all (not only the ordinary 50 results) results from the LTA APIs
    
    @Input:
    url: URL corresponding to the desired API
    
    url_speed_band = "http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBands"    
    url_bus_stops = "http://datamall2.mytransport.sg/ltaodataservice/BusStops"    
    url_incident = "http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"    
    url_taxi = "http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability"
    
    @Output
    dictionary: each url gives obviously a different structure
    
    """
    results  =  []
    while True:
        new_results  =  requests.get(
            url,
            headers = headers,
            params = {'$skip': len(results)}
        ).json()['value']
        if new_results  ==  []:
            break
        else:
            results +=  new_results
    return results


def fetch_50(url): 
    """Retrieve just 50 results from LTA APIs
    
    """ 
    results =  requests.get(url,headers = headers).json()  
    return results
    
# ------------------------------------------------------------------------------
#                        JSON tools
# ------------------------------------------------------------------------------   


def loadJSON(fileName):
    """
    
    @Input
    fileName: JSON file (do not add the extension)
    
    """
    return json.loads(open(fileName).read())


def writingJSON(fileName,res):
    """
    
    @Input
    fileName: name of the output file do not include extension
    """
    with open(fileName+'.json', "w") as f:
        f.write(json.dumps(res))
    
    return 0
    
# ------------------------------------------------------------------------------
#            Formating data
#  
# ------------------------------------------------------------------------------


def formatDate(string):
    """Give an integer as a date. DDMMYY
    
    """
    splitStr = re.split('-',string)
    return int(splitStr[0]+'12'+splitStr[2])


def formatAddress():
    """Retrieve all the visited addresses and return a set of it, sorted by alphabetical order
    
    """
    # Strings to load data
    stringFile = '/Users/Louis/Documents/Research/Code/cleanedData/'
    days = {'cleaned01-Dec-2015':2,# tuesday
        'cleaned02-Dec-2015':3,# wednesday
        'cleaned03-Dec-2015':4,# ...
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
        
    # Store results
    addresses = []
    CourierSuppliedAddresses = []
     
    for day in days.keys():
        # Configuration for CSV reading
        with open(stringFile+day+'_modified.csv') as csvfile:
            # Dictionary containing the info
            reader = csv.DictReader(csvfile,delimiter = ',')
            # print(day)
            
            for row in reader:
                addresses.append(row['Address'])
                CourierSuppliedAddresses.append(row['CourierSuppliedAddress'])
                
    addresses = list(set(addresses))
    addresses.sort()
    
    CourierSuppliedAddresses  =  list(set(CourierSuppliedAddresses))
    CourierSuppliedAddresses.sort()
    return addresses, CourierSuppliedAddresses
    
    
def formatPickup(string):
    """Return an int when it's not 'N/A' and O otherwise
    
    """
    if string == 'N/A':
        return 0
    else:
        return int(string)
        
        
def formatCoordinates(string):
    """Return a float when it's not 'N/A' and O otherwise
    
    """
    if string == 'N/A':
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
    if string  ==  'N/A':
        return 0
    elif string  ==  'D':
        return 1
    elif string  ==  'M':
        return 2
        
    elif string  ==  'C':
        return 3
        
    elif string  ==  'R':
        return 4
        
    else:
        return 5
        
        
if __name__  ==  "__main__":
    
    url_speed_band = "http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBands"    
    url_bus_stops = "http://datamall2.mytransport.sg/ltaodataservice/BusStops"    
    url_incident = "http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"    
    url_taxi = "http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability"
    
    res = fetch_50("http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBands")
    writingJSON('speedDatcvccxa',res)
    print(res['value'][0].keys())