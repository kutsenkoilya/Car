# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 01:28:05 2018

@author: Илья
"""

#DETECTION RANGE
LineRange = 30
CriticalWallRange = 30 #в сантиметрах
WallRange = 10
ParkingDistance = 10

#CAMERA SETTINGS
PiCameraResH = 240
PiCameraResW = 320
PiCameraFrameRate = 32
RecEnabled = 0

#MOVEMENT SETTINGS
DefaultAngle = 90
RightTurnAngle = 115
LeftTurnAngle = 65
RightToLeftDegree = 105
LeftToRightDegree = 75
Stop = 10
MoveSpeed = 125
StartSpeed = 125



#RightLane SETTINGS
CroppedH = int(PiCameraResH/2)
CroppedW = int(PiCameraResW/2)
LaneMaxW = int(CroppedW/10)
SensorStep = 40

