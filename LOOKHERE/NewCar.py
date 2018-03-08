# -*- coding: utf-8 -*-

import Map
import LineDetector
import CarControl
from Detector import Detector
import cv2
import time
import numpy as np

from picamera.array import PiRGBArray
from picamera import PiCamera

import CarSettings as CarSettings


class Car:  # основные методы, которые будут использоваться на соревнованиях speedy_road,city_road,parking, circle_road
    def __init__(self, device):  # тут бы по хорошему проинициализировать все что у нас написано
        self.CarCon = CarControl.CarControl(device)  # кар контролу передаем девайс которым пользуемся
        self.Detector=  Detector()
        self.Road = 0
        self.map = Map.MyMap(open('graph.txt'))  # нам нужна карта для построения маршрута
        self.Path = []
        self.prev = 0
        self.startDot = 1
        self.finishDot = 18
        self.bluesigns= 0
        self.walls = [10000, 10000, 10000]
        self.lines = [10000,10000,10000]
        self.frame = np.array([])
        self.RedIsON = 0
        self.brick = 0
        self.camera = PiCamera()
        self.camera.resolution = (CarSettings.PiCameraResW, CarSettings.PiCameraResH)
        self.camera.framerate = CarSettings.PiCameraFrameRate
        self.camera.vflip = True
        self.camera.hflip = True
        self.rawCapture = PiRGBArray(self.camera, size=(CarSettings.PiCameraResW, CarSettings.PiCameraResH))
        self.crossroad = False
        self.fullcross = False
    def light_handler(self):
        while self.RedIsON:
            self.CarCon.move(0,CarSettings.Stop)
            pass
        return

    def brick_handler(self, joint):
        prev = 0
        for j in self.Path:
            if prev == joint:
                if map.GetTurnDirecion(prev, joint) == 0:
                    joint.delete()
                    return 1
            prev = j
        return 0

    def blue_sign_handler(self, sign, joint):  # метод обработки знаков для городской дороги
        prev = 0  # пример обработки можно внести исправления
        if sign == 3:  # движение вперед
            for j in self.Path:
                if prev == joint:
                    if map.GetTurnDirecion(prev, joint) != 0:
                        joint.delete()
                        return 1
                prev = j

        elif sign == 4:  # направо
            for j in self.Path:
                if prev == joint:
                    if map.GetTurnDirection(prev, joint) != 1:
                        joint.delete()
                        return 1
                prev = j
            pass
        elif sign == 5:  # налево
            for j in self.Path:
                if prev == joint:
                    if map.GetTurnDirection(prev, joint) != -1:
                        joint.delete()
                        return 1
                prev = j
            pass
        elif sign == 6:  # прямо или направо
            for j in self.Path:
                if prev == joint:
                    if map.GetTurnDirection(prev, joint) != 1 and map.GetTurnDirecion(prev, joint) != 0:
                        joint.delete()
                        return 1
                prev = j
            pass
        elif sign == 7:  # прямо или налево
            for j in self.Path:
                if prev == joint:
                    if map.GetTurnDirection(prev, joint) != -1 and map.GetTurnDirecion(prev, joint) != 0:
                        joint.delete()
                        return 1
                prev = j
            pass
        return 0

    def turn_on(self, direction): # переезд перекрестка
        if direction == 0:  # едем прямо
            while self.crossroad:
                self.CarCon.move(1,CarSettings.MoveSpeed)
        if direction == 1:  # поворот вправо
            while self.crossroad:
                self.CarCon.move(1,CarSettings.MoveSpeed)
                self.CarCon.turn(CarSettings.RightTurnAngle)
        if direction == -1:  # поворот влево
            while self.crossroad:
                self.CarCon.move(1,CarSettings.MoveSpeed)
                self.CarCon.turn(CarSettings.LeftTurnAngle)
        if direction == -2:  # разворот
            while self.crossroad:
                self.CarCon.turn(CarSettings.LeftTurnAngle)
                self.CarCon.move(1,CarSettings.MoveSpeed)
                self.CarCon.turn(CarSettings.LeftTurnAngle)
                self.CarCon.move(1,CarSettings.MoveSpeed)

        return

    def simple_line(self):  # езда по скоростной
        vecs = [[-3, -1, 70], [3, -1, 70]]
        self.Road = LineDetector.RoadControl(self.frame, 240, vecs, viz=False)
        
        while not self.crossroad and self.bluesigns == 0:
            for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
                    image = frame.array
            cop = self.CarCon.getDistance()
            for i in range (3):
                if type(cop[i]) == type(None):
                    self.walls[i]=10000
                else:
                    self.walls[i]=cop[i]
            self.walls = self.CarCon.getDistance()
            if self.walls[0] < CarSettings.WallRange or self.walls[2] < CarSettings.WallRange:  # подставить константы
                self.crossroad = True
            else:
                self.crossroad = False
            if self.walls[0] < CarSettings.WallRange and self.walls[2] < CarSettings.WallRange:  # подставить константы
                self.fullcross = True
            else:
                self.fullcross = False
            
            
            self.Road.img=image.copy()
            self.lines = self.Road.poke()
            self.brick = self.Detector.DetectRedSign(image, False)
            self.bluesigns = self.Detector.DetectBlueSign(self.frame, False)
            self.RedIsON = self.Detector.DetectTrLight(self.frame, False)
            self.light_handler()
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
                if self.lines[0] < CarSettings.LineRange or self.walls[0] < CarSettings.WallRange:  # отъезжаем от стены или от линии подобрать константы
                    self.CarCon.turn(CarSettings.LeftToRightDegree)  # угол настроить
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    pass
                if self.lines[1] < CarSettings.LineRange or self.walls[2] < CarSettings.WallRange:  #
                    self.CarCon.turn(CarSettings.RightToLeftDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    pass
                else:
                    self.CarCon.move(1,CarSettings.MoveSpeed)  # прямо
            self.rawCapture.truncate(0)
            cv2.destroyAllWindows()
            
        return self.bluesigns  # иначе завершаем движение и выдаем знак
    
            
            
        		
    def moving_on_line(self, joint):  # двигаемся по маршруту
       
        while not self.crossroad:  # проверяем что ничего нового не встретилось
            for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
                    image = frame.array
            cop = self.CarCon.getDistance()
            for i in range (3):
                if type(cop[i]) == type(None):
                    self.walls[i]=10000
                else:
                    self.walls[i]=cop[i]
            self.walls = self.CarCon.getDistance()
            if self.walls[0] < CarSettings.WallRange or self.walls[2] < CarSettings.WallRange:  # подставить константы
                self.crossroad = True
            else:
                self.crossroad = False
            if self.walls[0] < CarSettings.WallRange and self.walls[2] < CarSettings.WallRange:  # подставить константы
                self.fullcross = True
            else:
                self.fullcross = False
            
            
            self.Road.img=image.copy()
            self.lines = self.Road.poke()
            self.brick = self.Detector.DetectRedSign(image, False)
            self.bluesigns = self.Detector.DetectBlueSign(image, False)
            self.RedIsON = self.Detector.DetectTrLight(image, False)
            
            self.light_handler()
            if self.brick:
                self.brick_handler(joint)
                return 1
            elif self.bluesigns != 0:
                return self.bluesigns
            else:
                if self.walls[1]<CarSettings.WallRange:
                    if self.walls[0]>CarSettings.WallRange:
                        self.CarCon.turn(CarSettings.RightToLeftDegree)
                        self.CarCon.move(1,CarSettings.MoveSpeed)
                        self.CarCon.turn(CarSettings.DefaultAngle)
                    elif self.walls[2]>CarSettings.WallRange:
                        self.CarCon.turn(Car.LeftToRightDegree)
                        self.CarCon.move(1,CarSettings.MoveSpeed)
                        self.CarCon.turn(CarSettings.DefaultAngle)
                    else:
                        self.CarCon.move(0,CarSettings.Stop)
                        return
                if self.lines[0] < CarSettings.LineRange or self.walls[0] < CarSettings.WallRange:  # отъезжаем от стены или от линии подобрать константы
                    self.CarCon.turn(CarSettings.LeftToRightDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    self.CarCon.turn(CarSettings.DefaultAngle)
                    pass
                elif self.lines[1] < CarSettings.LineRange or self.walls[2] < CarSettings.WallRange:  #
                    self.CarCon.turn(CarSettings.RightToLeftDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    self.CarCon.turn(CarSettings.DefaultAngle)
                    pass
                else:
                    self.CarCon.move(1,CarSettings.MoveSpeed)  # прямо
        self.rawCapture.truncate(0)
        cv2.destroyAllWindows()


        return 0  # доехали без проблем до перекрестка или нет?

    def speedy_road(self):  # просто едем по по линии и поворачиваем на первых? поворотах направо... Всё отлично!!
       
        
        self.simple_line()  # держимся нашей прямой
        if self.bluesigns == 6 or self.crossroad or self.bluesigns==4:  # поворот направо
            # на самом деле достаточно знать только что правый поворот открыт
            self.turn_on(1)
        self.simple_line()
        if self.bluesigns == 3:
            self.turn_on(0)
            self.startDot = 1
        else:
            self.startDot = 9
            self.turn_on(1)

        return 1  # по идее должна вернуть значение обозначающее на каком повороте мы заехали

    def city_road(self):

        for joint in self.map.joints: # -2 если на втором повороте заехали, -1 если на первом для ключей
            if joint.leftDot.id == self.startDot:
                self.prev = joint
        for dot in self.map.dots:
            if dot.id == self.startDot:
                self.startDot = dot
            if dot.id == self.finishDot:
                self.finishDot = dot
        self.Path = self.map.FindTheWay(self.startDot, self.finishDot)  # теперь наш путь лежит в path
        # идея такая пытаемся поехать в нужном направлении не получилось удаляем ребро, по новой считаем
        while self.startDot != self.finishDot:  # пока не доехали до финиша
            for joint in self.Path:
                direction = self.map.GetTurnDirection(self.prev, joint)  # смотрим направление поворота
                self.prev = joint  # для вычисления следующего направления запоминаем ребро по которому поехали
                self.Car.turn_on(direction)
                sign = self.moving_on_line(joint)  # поворачиваем на повороте 0 прямо 1 право -1 влево -2 разворот
                if sign:  # едем и держимся линии пока ничего не мешает
                    if sign == 1:
                        changed = self.brick_handler(joint)
                    else:
                        changed = self.blue_sign_handler(sign, joint)
                    if changed:
                        break
                elif not self.crossroad:  # если что-то помешало придется вернутся и перестроить маршрут
                    joint.Delete()
                    self.turn_on(-2) # придется развернутся -2 разворот
                    break
                else:
                    self.startDot = joint.GetNegative(self.startDot)  # если оказались на перекрестке продолжаем движение
            self.Path = self.map.FindTheWay(self.startDot, self.finishDot)
    
        return 2


    def circle_road(self):
        
        self.CarCon.move(1,CarSettings.MoveSpeed)
        self.CarCon.turn(CarSettings.DefaultAngle)
        self.CarCon.move(1,CarSettings.MoveSpeed)
        while not self.crossroad: # проверяем что ничего нового не встретилось
            if self.lines[0] or self.walls[0]:  # отъезжаем от стены или от линии подобрать константы
                self.CarCon.move(1,CarSettings.MoveSpeed)
                self.CarCon.turn(CarSettings.RightTurnAngle)
                pass
                # отворачиваем
            if self.lines[1] or self.walls[2]:  #
                self.CarCon.move(1,CarSettings.MoveSpeed)
                self.CarCon.turn(CarSettings.LeftTurnAngle)
                pass
                # отворачиваем
            else:
                self.CarCon.move(1,CarSettings.MoveSpeed) # прямо
         
        return 3




    def parking(self):
        self.parking = True
        
        while self.ParkingDis > CarSettings.ParkingDistance:  # подъезжаем
            self.CarCon.move()
        
        # паркуемся
        

        return 4
    
