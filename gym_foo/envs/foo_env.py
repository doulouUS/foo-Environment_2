# -*- coding: utf-8 -*-
"""
Created on Wed Jan  11 10:10:58 2017

@author: Louis DOUGE
"""


import numpy as np

import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym.envs.toy_text import discrete

class FooEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        ## Build a DiscreteEnv object
        #Number of state
        nS=10
        #Number of actions
        nA=10
        #Transitions (*)
        P = {s : {a : [] for a in range(nA)} for s in range(nS)}

        #Initial State distribution     
        isd = np.zeros(nS)

        #(*) dictionary dict of dicts of lists, where 
        #P[s][a] == [(probability, nextstate, reward, done), ...]
        
        
        #DiscreteEnv object 
        discrete.DiscreteEnv.__init__(self, nS, nA, P, isd)
        
        ## Specific members of FooEnv
                
        
        
        
        return 0    
    
    def _step(self, action):
        ...
    def _reset(self):
        ...
    def _render(self, mode='human', close=False):
        ...
