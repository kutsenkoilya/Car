# -*- coding: utf-8 -*-

import Map
import LineDetector
import CarControl
from Detector import Detector
from threading import Thread
import cv2
import time
import numpy as np

from picamera.array import PiRGBArray
from picamera import PiCamera

import CarSettings as CarSettings


class Car:  # основные методы, которые будут использоваться на соревнованиях speedy_road,city_road,parking, circle_road
    def __init__(self, device):  # тут бы по хорошему проинициализировать все что у нас написано
        self.CarCon = CarControl.CarControl(device)  # кар контролу передаем девайс которым пользуемся
        self.SignThread = self.SignThread()
        self.LineDet = self.LineThread()
        self.CW = self.CameraWrapper(self.LineDet, self.SignThread)
        self.WallDet = self.WallThread(self.CarCon)  # детектор стен
        self.map = Map.MyMap(open('graph.txt'))  # нам нужна карта для построения маршрута
        self.Path = []
        self.prev = 0
        self.startDot = 1
        self.finishDot = 18

    class CameraWrapper(Thread):
        def __init__(self, l, t):
            Thread.__init__(self)
            self.camera = PiCamera()
            self.camera.resolution = (CarSettings.PiCameraResW, CarSettings.PiCameraResH)
            self.camera.framerate = CarSettings.PiCameraFrameRate
            self.camera.vflip = True
            self.camera.hflip = True
            self.rawCapture = PiRGBArray(self.camera, size=(CarSettings.PiCameraResW, CarSettings.PiCameraResH))
            self.image = 0
            self.mark = False
            self.L = l  #
            self.T = t  # лайн и сайн детектор соответственно

        def run(self):  # dsf
            self.mark = True
            while (self.mark):
                for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
                    image = frame.array
                    print(image.shape)
                    image.copy()
                    self.T.frame = image
                    k = cv2.waitKey(30) & 0xff
                    if k == 27:
                        break;

                    # очистка кадра. важная штука!
                    self.rawCapture.truncate(0)
        
            cv2.destroyAllWindows()

        def off(self):
            self.mark = False

    class SignThread(Thread):  # поток для детектирования знаков и ситуаций на дороге
        def __init__(self):
            Thread.__init__(self)
            self.Detector = Detector()
            self.bluesigns = 0
            self.RedIsON = False
            self.mark = False
            self.frame = np.array([])
            self.brick = 0

        def run(self):  # по задумке 0-прямая дорога, 1-перекресток, 2-знак,3-препятствие
            self.mark = True
            while self.mark:
                if len(self.frame)>0:
                    self.brick = self.Detector.DetectRedSign(self.frame, False)
                    self.bluesigns = self.Detector.DetectBlueSign(self.frame, False)
                    self.RedIsON = self.Detector.DetectTrLight(self.frame, False)
                    # 3 - движение вперед 4 - направо 5 - налево 6 - прямо или направо 7 - прямо или налево

        def off(self):
            self.mark = False

    class LineThread(Thread):  # поток для детектирования полос
        def __init__(self):
            Thread.__init__(self)
            self.lines = 0
            self.mark = False
            self.parking = False
            self.frame = np.array([])
            self.Road = 0
            self.ParkingDis = 0

        def run(self):
            
            self.mark = True
            vecs = [[-3, -1, 70], [3, -1, 70]]
            self.Road = LineDetector.RoadControl(self.frame, 240, vecs, viz=True)
            if not self.parking:
                while self.mark:
                    if len(self.frame)>0:
                        self.lines = self.Road.poke(self.frame)
            else:
                while self.mark:
                    if len(self.frame)>0:
                        self.ParkingDis = self.Road.poke(self.frame)
                    
                    
                    
                    
                    
                    
                    pass
                    # detect parking

        def off(self):
            self.mark = False

    class WallThread(Thread):  # поток для детектирования стен
        def __init__(self,control):
            Thread.__init__(self)
            self.WD = control
            self.walls = [0,0,0]  # 0 слева 1 спереди 2 справа
            self.mark = False
            self.crossroad = False
            self.fullcross = False

        def run(self):
            self.mark = True
            self.walls = self.WD.getDistance()

            while self.mark:
                self.walls = self.WD.getDistance()
                if self.walls[0] < CarSettings.WallRange or self.walls[2] < CarSettings.WallRange:  # подставить константы
                    self.crossroad = True
                else:
                    self.crossroad = False
                if self.walls[0] < CarSettings.WallRange and self.walls[2] < CarSettings.WallRange:  # подставить константы
                    self.fullcross = True
                else:
                    self.fullcross = False

        def off(self):
            self.mark = False

    def light_handler(self):
        while self.SignThread.RedIsON:
            self.CarCon.move(0,CarSetting.Stop)
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
            while self.WallDet.crossroad:
                self.CarCon.move(1,CarSettings.MoveSpeed)
        if direction == 1:  # поворот вправо
            while self.WallDet.crossroad:
                self.CarCon.move(1,CarSettings.MoveSpeed)
                self.CarCon.turn(CarSettings.RightTurnAngle)
        if direction == -1:  # поворот влево
            while self.WallDet.crossroad:
                self.CarCon.move(1,CarSettings.MoveSpeed)
                self.CarCon.turn(CarSettings.LeftTurnAngle)
        if direction == -2:  # разворот
            while self.WallDet.crossroad:
                self.CarCon.turn(CarSettings.LeftTurnAngle)
                self.CarCon.move(1,CarSettings.MoveSpeed)
                self.CarCon.turn(CarSettings.LeftTurnAngle)
                self.CarCon.move(1,CarSettings.MoveSpeed)

        return

    def simple_line(self):  # езда по скоростной
        while not self.WallDet.crossroad and self.SignThread.bluesigns == 0:
            self.light_handler()
            if self.WallDet.walls[1]<CarSettings.WallRange:
                if self.WallDet.walls[0]>CarSettings.WallRange:
                    self.CarCon.turn(CarSettings.RightToLeftDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    self.CarCon.turn(CarSettings.DefaultAngle)
                else:
                    self.CarCon.turn(CarSettings.RightToLeftDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    self.CarCon.turn(CarSettings.DefaultAngle)
            else:
                if self.LineDet.lines[0] < CarSettings.LineRange or self.WallDet.walls[0] < CarSettings.WallRange:  # отъезжаем от стены или от линии подобрать константы
                    self.CarCon.turn(CarSettings.LeftToRightDegree)  # угол настроить
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    pass
                if self.LineDet.lines[1] < CarSettings.LineRange or self.WallDet.walls[2] < CarSettings.WallRange:  #
                    self.CarCon.turn(CarSettings.RightToLeftDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    pass
                else:
                    self.CarCon.move(1,CarSettings.MoveSpeed)  # прямо
        return self.SignThread.bluesigns  # иначе завершаем движение и выдаем знак

    def moving_on_line(self, joint):  # двигаемся по маршруту
        while not self.WallDet.crossroad:  # проверяем что ничего нового не встретилось
            self.light_handler()
            if self.SignThread.brick:
                self.brick_handler(joint)
                return 1
            elif self.SignThread.bluesigns != 0:
                return self.SignThread.bluesigns
            else:
                if self.WallDet.walls[1]<CarSettings.WallRange:
                    if self.WallDet.walls[0]>CarSettings.WallRange:
                        self.CarCon.turn(CarSettings.RightToLeftDegree)
                        self.CarCon.move(1,CarSettings.MoveSpeed)
                        self.CarCon.turn(CarSettings.DefaultAngle)
                    elif self.WallDet.walls[2]>CarSettings.WallRange:
                        self.CarCon.turn(Car.LeftToRightDegree)
                        self.CarCon.move(1,CarSettings.MoveSpeed)
                        self.CarCon.turn(CarSettings.DefaultAngle)
                    else:
                        return
                if self.LineDet.lines[0] < CarSettings.LineRange or self.WallDet.walls[0] < CarSettings.WallRange:  # отъезжаем от стены или от линии подобрать константы
                    self.CarCon.turn(CarSettings.LeftToRightDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    self.CarCon.turn(CarSettings.DefaultAngle)
                    pass
                elif self.LineDet.lines[1] < CarSettings.LineRange or self.WallDet.walls[2] < CarSettings.WallRange:  #
                    self.CarCon.turn(CarSettings.RightToLeftDegree)
                    self.CarCon.move(1,CarSettings.MoveSpeed)
                    self.CarCon.turn(CarSettings.DefaultAngle)
                    pass
                else:
                    self.CarCon.move(1,CarSettings.MoveSpeed)  # прямо

        return 0  # доехали без проблем до перекрестка или нет?

    def speedy_road(self):  # просто едем по по линии и поворачиваем на первых? поворотах направо... Всё отлично!!
        self.CW.start()
        self.WallDet.start()
        self.SignThread.start()
        self.LineDet.start()
        self.simple_line()  # держимся нашей прямой
        if self.SignThread.bluesigns == 6 or self.WallDet.crossroad or self.SignThread.bluesigns==4:  # поворот направо
            # на самом деле достаточно знать только что правый поворот открыт
            self.turn_on(1)
        self.simple_line()
        if self.SignThread.bluesigns == 3:
            self.turn_on(0)
            self.startDot = 1
        else:
            self.startDot = 9
            self.turn_on(1)
        self.SignThread.off()
        self.LineDet.off()
        self.WallDet.off()
        self.CW.off()
        return 1  # по идее должна вернуть значение обозначающее на каком повороте мы заехали

    def city_road(self):
        self.CW.start()
        self.WallDet.start()
        self.SignThread.start()
        self.LineDet.start()

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
                elif not self.WallDet.crossroad:  # если что-то помешало придется вернутся и перестроить маршрут
                    joint.Delete()
                    self.turn_on(-2) # придется развернутся -2 разворот
                    break
                else:
                    self.startDot = joint.GetNegative(self.startDot)  # если оказались на перекрестке продолжаем движение
            self.Path = self.map.FindTheWay(self.startDot, self.finishDot)
        self.CW.off()
        self.WallDet.off()
        self.SignThread.off()
        self.LineDet.off()
        return 2


    def circle_road(self):
        self.CW.start()
        self.LineDet.start()
        self.WallDet.start()
        
        
        self.CarCon.move()
        self.CarCon.turn()
        self.CarCon.move()
        while not self.WallDet.crossroad: # проверяем что ничего нового не встретилось
            if self.LineDet.lines[0] or self.walls[0]:  # отъезжаем от стены или от линии подобрать константы
                self.CarCon.move(1,CarSettings.MoveSpeed)
                self.CarCon.turn(CarSettings.RightTurnAngle)
                pass
                # отворачиваем
            if self.LineDet.lines[1] or self.walls[2]:  #
                self.CarCon.move(1,CarSettings.MoveSpeed)
                self.CarCon.turn(CarSettings.LeftTurnAngle)
                pass
                # отворачиваем
            else:
                self.CarCon.move(1,CarSettings.MoveSpeed) # прямо
         
        self.CW.off()
        self.LineDet.off()
        self.WallDet.off()
        return 3




    def parking(self):
        self.CW.start()
        self.WallDet.start()
        self.LineDet.parking = True
        self.LineDet.start()
        
        while self.LineDet.ParkingDis > CarSettings.ParkingDistance:  # подъезжаем
            self.CarCon.move()
        
        # паркуемся
        
        self.CW.off()
        self.WallDet.off()
        self.LineDet.off()
        return 4





