# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 14:30:28 2017

@author: Louis
"""

import numpy as np
import requests

from fooTools import *


class fedexGraph():
    """All in one container of a task possibly done by one delivery van.
    It includes info plus methods to work on these data.
    
    """
    
    def __init__(self, npArray):
        #np array containing all the info given by fedex
        # ['StopDate','WeekDay','StopOrder','StopStartTime','Address','PostalCode',
        #'CourierSuppliedAddress','ReadyTimePickup','CloseTimePickup','PickupType',
        #'WrongDayLateCount','RightDayLateCount','FedExID','Longitude','Latitude']
        self.data=npArray 
        
        #----------------------- Addresses ---------------------------------
        self.globaladdress, self.globalCourierSuppliedAddress=formatAddress()
        self.Address=list(set(npArray[:,4]))
       
        
        #----------------------- API matters ---------------------------------
        # LTA
        self.ltaKey="8Q6acuQNTAGl8r/GqViFtA=="
        self.UniqueUserID='8ecabd56-08a2-e843-0a7a-9944dccf124a'
        # Headers
        self.ltaHeaders = {
            'AccountKey': self.ltaKey,
            'UniqueUserID': self.UniqueUserID,
            'accept': 'application/json'
        }
        
        # Bing
        self.bingKey="Avah46_M-gfFeQ3P1w09Qq1ElAV9ZEHFDm9b8JRCRa8qPP5uVn21hDqAPVJgV4i_"
                
                
        
    def nbPickup(self):
        """Nb of pickups
        """
        
        mask= self.data[:,7]!='N/A'
        return self.data[mask].shape
        
    def nbDeliv(self):
        """Nb of deliveries
        """
        
        mask= self.data[:,7]=='N/A'
        return self.data[mask].shape
        

data=np.loadtxt('demand_models/fedex.data')
mask=(data[:,0] == 11215) #date
data=data[mask]
data=data[102:137,:]#cluster5 1 dec

taskCluster=fedexGraph(data)
print(taskCluster.addresses[int(data[0,4])])
print(taskCluster.addresses[int(data[1,4])])

g1,g2,g3,g4,g5,roadNames,g6,g7,maneuvType,coordPath=roadSegments([taskCluster.addresses[int(data[0,4])],taskCluster.addresses[int(data[1,4])]])
print(roadNames)
print(maneuvType)
print(coordPath)
 
            