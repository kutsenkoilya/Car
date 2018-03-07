# -*- coding: utf-8 -*-
from Car import Car
import time

time.sleep(5)
Carry=Car("/dev/ttyUSB0") #создаем машинку
Carry.Road()
