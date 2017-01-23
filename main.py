# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 13:41:00 2017

@author: Louis
"""

from dynamics.fooTools import *
import schedule
import time


if __name__ == "__main__":
    
    url_speed_band="http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBands"    
    url_bus_stops="http://datamall2.mytransport.sg/ltaodataservice/BusStops"    
    url_incident="http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"    
    url_taxi="http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability"    

    
    def job():   
        res = fetch_50(url_speed_band)
        stringTime=time.strftime("%Hh%M-%d-%m-%Y")
        writingJSON(stringTime,res)
    #mem=loadJSON('res_50.json') 
    schedule.every(1).minutes.do(job)
#schedule.every().hour.do(job)
#schedule.every().day.at("10:30").do(job)
#schedule.every().monday.do(job)
#schedule.every().wednesday.at("13:15").do(job)

    while True:
        schedule.run_pending()
        print('Job done once at '+time.strftime("%H:%M"))
        time.sleep(60)
        
        