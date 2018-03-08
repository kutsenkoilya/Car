# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 12:12:23 2018

@author: Илья
"""

import cv2
import time
import numpy as np
import CarSettings
from picamera.array import PiRGBArray
from picamera import PiCamera


camera = PiCamera()
camera.resolution = (CarSettings.PiCameraResW, CarSettings.PiCameraResH)
camera.framerate = CarSettings.PiCameraFrameRate
camera.vflip = True
camera.hflip = True
rawCapture = PiRGBArray(camera, size=(CarSettings.PiCameraResW, CarSettings.PiCameraResH))
print (camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)[0])