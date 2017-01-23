# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 13:41:00 2017

@author: Louis
"""

from dynamics.fooTools import *


if __name__ == "__main__":
    
    url_speed_band="http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBands"    
    url_bus_stops="http://datamall2.mytransport.sg/ltaodataservice/BusStops"    
    url_incident="http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"    
    url_taxi="http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability"
    
    res = fetch_50(url_speed_band)    
    #mem=loadJSON('res_50.json')
    
    print(res['value'][0].keys())