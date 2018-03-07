# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 01:28:05 2018

@author: Илья
"""

#DETECTION RANGE
DefaultAngle = 0
CriticalWallRange =30 #в сантиметрах
WallRange = 100
ParkingDistance = 10

#CAMERA SETTINGS
PiCameraResH = 240
PiCameraResW = 320
PiCameraFrameRate = 32
RecEnabled = 0

#MOVEMENT SETTINGS
Stop = 10
RightToLeftDegree = 30
LeftToRightDegree = 30
MoveSpeed = 125
StartSpeed = 125
RightTurnAngle = 90
LeftTurnAngle = -90


#RightLane SETTINGS
CroppedH = int(PiCameraResH/2)
CroppedW = int(PiCameraResW/2)
LaneMaxW = int(CroppedW/10)
SensorStep = 40

