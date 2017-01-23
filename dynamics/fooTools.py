# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 09:39:45 2017

@author: Louis


Toolbox necessary to build the dynamics of our environment
"""
import requests
import json
import csv
import urllib.parse
from urllib.parse import urlparse
#import httplib2 as http #External library

#Useful help
# https://github.com/hiimivantang/ltadatamallcrawler

#------------------------------------------------------------------------------
#                       APIs
#------------------------------------------------------------------------------
# LTA
AccountKey="8Q6acuQNTAGl8r/GqViFtA=="
UniqueUserID='8ecabd56-08a2-e843-0a7a-9944dccf124a'
# Headers
headers = {
    'AccountKey': AccountKey,
    'UniqueUserID': UniqueUserID,
    'accept': 'application/json'
}

# Bing
API_Key="Avah46_M-gfFeQ3P1w09Qq1ElAV9ZEHFDm9b8JRCRa8qPP5uVn21hDqAPVJgV4i_"

#------------------------------------------------------------------------------
#                       Deliveries related
#------------------------------------------------------------------------------

def jobRetriever (string, nbTrucks, path):
    """Retrieve sequences of customers to visit and the pick-ups occuring
    when operating.
    
    @Input
    string: file's name of the day to process ex: cleaned01-Dec-2015.csv 
    (added to /Users/Louis/Documents/Research/Code/cleanedData/ to create a valid path)
    
    nbTrucks: nb of sequence to retrieve
    
    path: path where the data is located (cleanedData)
        on my mac:'/Users/Louis/Documents/Research/Code/cleanedData/'
    
    @Ouput
    dicionary {'cluster_n':{'delivery_m':[Address,Longitude,Latitude]}}
    """
    
    dictio={'date': string[7:18]}    
    
    #Configuration for CSV reading
    with open(path+string) as csvfile:
        #Dictionary containing the info
        reader=csv.DictReader(csvfile,delimiter=',')
        
        # Keep track of numbers
        clusterNb=0 # sequences
        deliveryNb=1 
        pickUpNb=1
        
        dictSeq={'Init' : [None,None,None]}
        
        for row in reader:
            
            if row['StopOrder']=='1' : # start of a new sequence
                
                
                dictio['cluster_'+str(clusterNb)]= dictSeq.copy()
                clusterNb+=1
                if clusterNb==nbTrucks+1:
                    break
                # Initialization

                dictSeq.clear()
                deliveryNb=1
                pickUpNb=1 
        
                if row['ReadyTimePickup']=='N/A': # type: delivery
                
                    dictSeq['delivery_'+str(deliveryNb)]= [row['Address'],\
                    row['Longitude'],row['Latitude']]
                    deliveryNb+=1
                else:
            
                    dictSeq['pickUp_'+str(pickUpNb)]= [row['Address'],\
                    row['Longitude'],row['Latitude'],row['ReadyTimePickup'],row['CloseTimePickup']]
                    pickUpNb+=1
            else:
                
                if row['ReadyTimePickup']=='N/A': # type: delivery
                
                    dictSeq['delivery_'+str(deliveryNb)]= [row['Address'],\
                    row['Longitude'],row['Latitude']]
                    deliveryNb+=1
                else:
                    
                    dictSeq['pickUp_'+str(pickUpNb)]= [row['Address'],\
                    row['Longitude'],row['Latitude'],row['ReadyTimePickup'],row['CloseTimePickup']]
                    pickUpNb+=1

                                    
    return dictio   

result=jobRetriever('cleaned01-Dec-2015.csv',3,'/Users/Louis/Documents/Research/Code/cleanedData/')

def jobRetrieverToCSV(result,name,clusterNb=1):
    """Send jobRetriever results into a csv file
    
    @Input
    result: dictionary
    name: string to name the output csv file (do not add .csv)
    clusterNb: choose which cluster to write down (default 1)
    
    @Output
    csv file with following header
    Address   Longitude   Latitude   Type   ReadyTime   EndTime
    
    """
    with open(name+'.csv', 'w') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, ['Address','Longitude','Latitude','Type','ReadyTime','EndTime'])
        w.writeheader()
        for loc in result['cluster_'+clusterNb].items():
            if loc[1][1]!='N/A':# make sure we have the coordinates
                
                if loc[0][0]=='p': #pick-up
                    w.writerow({'Address':loc[1][0],'Longitude':loc[1][1],\
                    'Latitude':loc[1][2],'Type':'p','ReadyTime':loc[1][3],'EndTime':loc[1][4]})
                else:#delivery
                    w.writerow({'Address':loc[1][0],'Longitude':loc[1][1],\
                    'Latitude':loc[1][2],'Type':'d','ReadyTime':'None','EndTime':'None'})

#print(result['cluster_2']['delivery_1'])
#print(result['cluster_1']['delivery_1'])
#print(result['cluster_0']['Init'])

#------------------------------------------------------------------------------
#                       Routing related
#------------------------------------------------------------------------------
    
def roadSegments(locations):
    """Given a set of locations, return all the road segments joinning 
    these locations.
    
    Problem: limitations of the API (Google...)
    
    @Input
    locations: dictionnary-like ex: {clutser_1 :{'delivery_1' :[Address, Longitude, Latitude],
                                                'delivery_2' : [Address, Longitude, Latitude]}}
    
    @Output (tuples)
    statusCode  travelDistance   travelDuration   travelDurationTraffic (with traffic,
    not too sure about it)   numberSegments    itineraryItems
    """ 
    
    # Base URL
    uri = 'http://dev.virtualearth.net/' #Resource URL 
    path = 'REST/v1/Routes?'
    
    
    # URL Parameters
    params = { 'wayPoint.0' : locations[0],
               'wayPoint.1' : locations[1],
                'key' : API_Key}
                # by default 'optimize' : 'time'} #this is by default
    
    url=uri+path
        
    results= requests.get(
            url,
            params=params
        ).json()#['resourceSets']
        
    # Retrieving values
    statusCode=results['statusCode']
    travelDistance=results['resourceSets'][0]['resources'][0]['travelDistance']
    travelDuration=results['resourceSets'][0]['resources'][0]['travelDuration']
    travelDurationTraffic=results['resourceSets'][0]['resources'][0]['travelDurationTraffic']
    numberSegments=len(results['resourceSets'][0]['resources'][0]['routeLegs'][0]\
                    ['itineraryItems'])
    itineraryItems=results['resourceSets'][0]['resources'][0]['routeLegs'][0]\
                    ['itineraryItems']
    
    return statusCode,travelDistance,travelDuration,travelDurationTraffic,numberSegments,itineraryItems

#print(roadSegments(['Redmond, WA','Issaquah, WA']))
# Interesting values to retrieve

# Length browsed on this particular road
#print(resp['resourceSets'][0]['resources'][0]['routeLegs'][0]['itineraryItems']\
#                   [0]['travelDistance'])
# Duration of traveling on this segment (CAN BE REFINED USING TRAFFIC CONSIDERATIONS)
#print(resp['resourceSets'][0]['resources'][0]['routeLegs'][0]['itineraryItems']\
#                   [0]['travelDuration'])
   
#------------------------------------------------------------------------------
#                       LTA Data related
#------------------------------------------------------------------------------      

def fetch_all_lta(url):
    """Retrieve all (not only the ordinary 50 results) results from the LTA APIs
    
    @Input:
    url: URL corresponding to the desired API
    
    url_speed_band="http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBands"    
    url_bus_stops="http://datamall2.mytransport.sg/ltaodataservice/BusStops"    
    url_incident="http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"    
    url_taxi="http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability"
    
    @Output
    dictionary: each url gives obviously a different structure
    
    """
    results = []
    while True:
        new_results = requests.get(
            url,
            headers=headers,
            params={'$skip': len(results)}
        ).json()['value']
        if new_results == []:
            break
        else:
            results += new_results
    return results

def fetch_50(url): 
    """Retrieve just 50 results from LTA APIs
    
    """ 
    results= requests.get(url,headers=headers).json()  
    return results
    
#------------------------------------------------------------------------------
#                       JSON tools
#------------------------------------------------------------------------------   
    
def loadJSON(fileName):
    """
    
    @Input
    fileName: JSON file (add the extension)
    
    """
    return json.loads(open(fileName).read())
    
def writingJSON(fileName,res):
    """
    
    @Input
    fileName: name of the output file do not include extension
    res: dictionary-like result from fetch_  functions
    """
    with open(fileName+'.json', "w") as f:
        f.write(json.dumps(res))
    
    #return 0
    
#------------------------------------------------------------------------------
#                       TESTS
#------------------------------------------------------------------------------
    
#if __name__ == "__main__":
#    
#    url_speed_band="http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBands"    
#    url_bus_stops="http://datamall2.mytransport.sg/ltaodataservice/BusStops"    
#    url_incident="http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"    
#    url_taxi="http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability"
#    
#    res = fetch_50(url_speed_band)    
#    #mem=loadJSON('res_50.json')
#    
#    print(res['value'][0].keys())

                                