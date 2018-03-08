# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 13:29:45 2018

@author: Илья
"""
import CarSettings
from CarControl import CarControl




class Car:
    def __init__(self,device):
        self.CarCon=CarControl(device)
        self.crossroad=False
        self.fullcross=False
        self.walls=[10000,10000,10000]
        pass
    def nothing(self):
        while not self.fullcross:
            
            cop = self.CarCon.getDistance()
            for i in range (3):
                if type(cop[i]) == type(None):
                    self.walls[i]=10000
                else:
                    self.walls[i]=cop[i]
            self.walls = self.CarCon.getDistance()
            if self.walls[0] > CarSettings.WallRange  or self.walls[2] > CarSettings.WallRange :  # подставить константы
                self.crossroad = True
            else:
                self.crossroad = False
            if  self.walls[0] > CarSettings.WallRange and self.walls[2] > CarSettings.WallRange :  # подставить константы
                self.fullcross = True
            else:
                self.fullcross = False
            
            if self.walls[1]<CarSettings.WallRange:
                if self.walls[0]>CarSettings.WallRange:
                    self.CarCon.turn(CarSettings.RightToLeftDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    self.CarCon.turn(CarSettings.DefaultAngle)
                elif self.walls[1]>CarSettings.WallRange:
                    self.CarCon.turn(CarSettings.RightToLeftDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    self.CarCon.turn(CarSettings.DefaultAngle)
                else:
                    self.CarCon.move(0,CarSettings.Stop)
            else:
                if self.walls[0] < CarSettings.WallRange:  # отъезжаем от стены или от линии подобрать константы
                    self.CarCon.turn(CarSettings.LeftToRightDegree)  # угол настроить
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    pass
                if  self.walls[2] < CarSettings.WallRange:  #
                    self.CarCon.turn(CarSettings.RightToLeftDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    pass
                else:
                    self.CarCon.move(1,CarSettings.MoveSpeed)  # прямо
            
        return 1  # иначе завершаем движение и выдаем знак
        
    
    
        
        
    
    
    
    
    
    
    pass