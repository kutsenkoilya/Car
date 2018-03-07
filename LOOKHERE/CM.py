# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 00:42:10 2018

@author: Илья
"""
import time
from CarControl import CarControl
import CarSettings
class Car:
    def __init__(self,device):
        self.CarCon=CarControl(device)


    
    def Road(self):
        self.CarCon.move(1,125)
        while True:
            time.sleep(1)
            walls = self.CarCon.getDistance()
            print(walls[0],walls[1],walls[2])
            time.sleep(1)
           
            if walls[1]<CarSettings.CriticalWallRange:
                self.CarCon.move(0,CarSettings.Stop)
                break