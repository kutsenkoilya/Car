import Map
import LineDetector
import CarControl
from Detector import Detector
from threading import Thread
import cv2
import time

from picamera.array import PiRGBArray
from picamera import PiCamera

import CarSettings as CarSettings



class Car: #основные методы, которые будут использоваться на соревнованиях SpeedyRoad,CityRoad,Parking, CircleRoad
    def __init__(self,device): #тут бы по хорошему проинициализировать все что у нас написано
        self.CarCon=CarControl(device) # кар контролу передаем девайс которым пользуемся
        self.TroubleDet=self.SignThread()
        self.LineDet=self.LineChecking()
        self.CW=self.CameraWrapper(LineDet,TroubleDet)
        self.WallDet=self.WallThread(CarCon) #детектор стен
        



        self.prev=0
        self.startDot=0

    class CameraWrapper(Thread):
        def __init__(self,L,T):
            Thread.__init__(self)
            self.camera = PiCamera()
            self.camera.resolution = (CarSettings.PiCameraResW, CarSettings.PiCameraResH)
            self.camera.framerate = CarSettings.PiCameraFrameRate
            self.camera.vflip = True
            self.camera.hflip = True
            self.rawCapture = PiRGBArray(self.camera, size=(CarSettings.PiCameraResW, CarSettings.PiCameraResH))
            self.image=0
            self.mark=False
            self.L=L
            self.T=T


        def run(self):  #
            self.mark = True
            while (self.mark):
                for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):

                    image = frame.array
                    s.L.frame=image.copy()
                    s.T.frame=image
                    k = cv2.waitKey(30) & 0xff
                    if k == 27:
                        break;

                    # очистка кадра. важная штука!
                    self.rawCapture.truncate(0)

            cv2.destroyAllWindows()



            pass

    class SignThread(Thread):  #поток для детектирования знаков и ситуаций на дороге
        def __init__(self):
            Thread.__init__(self)
            self.Detector=Detector()
            self.signs = 0
            self.RedIsON=False
            self.mark=False
            self.frame=[]
            self.brick=0

        def run(self): # по задумке 0-прямая дорога, 1-перекресток, 2-знак,3-препятствие
            self.mark=True
            while (self.mark):
                    self.brick=self.Detecctor.DetectRedSign(self.frame, False)
                    self.signs = self.DetectBlueSign(self.frame, False)
                    self.RedIsON = self.Detector.DetectTrLight(self.frame, False) #1 - кирпич (красный знак стоп) 3 - движение вперед 4 - направо 5 - налево 6 - прямо или направо 7 - прямо или налево


    '''Конструктить'''
    class LineChecking(Thread):  #поток для детектирования полос
        def __init__(self,video_source):
            Thread.__init__(self)
            self.lines = 0
            self.mark=False
            self.parking=False
            self.frane=[]
            self.Road=0

        def run(self):
            
            self.mark=True
            if (not self.parking):
                vecs = [[-3, -1, 70], [3, -1, 70]]
                self.Road = LineDetector.RoadControl(self.frame, 240, vecs, viz=True)

                while (self.mark):
                    print(self.Road.poke(self.frame))
                    self.lines = self.Road.poke(self.frame)
            else:
                while (self.mark):
                    pass
                    #detect parking
                
                
                
              
    class WallThread(Thread):  #поток для детектирования стен
        def __init__(self,device):
            Thread.__init__(self)
            self.C=device
            self.walls = 0 #0 слева 1 спереди 2 справа
            self.mark=False
            self.WD=WallDetector()
            self.crossroad=false

        def run(self):
            self.mark=True
            self.walls = self.WD.Detect()

            while (self.mark):
                self.walls = self.WD.Detect()
                if (self.walls[] or self.walls[]): #подставить константы
                    self.crossroad=True
                else:
                    self.crossroad=False
              
            
            
    def SemaforHandler(self):
        while (self.TroubleDet.RedIsON):
            pass
        return

    '''разобраться со знаками'''
    def SignHandler(self,sign): #метод обработки знаков
        if (sign==1):#кирпич
            
            pass
        elif (sign==3):#движение вперед
            
            pass
        elif (sign == 4):#направо
            
            pass
        elif (sign == 5):#налево
            
            pass
        elif (sign == 6):#прямо или направо
            
            pass
        elif (sign == 7):#прямо или налево
            
            pass
        else:
            pass
        return



    '''метод проезда перекрестка'''
    def TurnOn(self,direction): # поворот
        if direction==0: #едем прямо
            while (NotCrossed): #как-то задетектить что мы проехали участок
                self.CarCon.move()
                self.CarCon.turn()
        if direction==1: #поворот вправо
            while (NotCrossed): #как-то задетектить что мы проехали участок
                self.CarCon.move()
                self.CarCon.turn()
        if direction==-1: #поворот влево
            while (NotCrossed): #как-то задетектить что мы проехали участок
                self.CarCon.move()
                self.CarCon.turn()
        if direction==-2: #разворот
            while (NotCrossed): #как-то задетектить что мы проехали участок
                self.CarCon.move()
                self.CarCon.turn()
        return



    def SimpleLine(self):#езда по скоростной
        while(not self.WallDet.crossroad and self.TroubleDet==0): #проверяем что ничего нового не встретилось
            self.SemaforHandler()
            if (self.LineDet.lines[0] or self.walls[0]): #отъезжаем от стены или от линии подобрать константы
                    self.CarCon.move()
                    pass
                    #отворачиваем
            if (self.LineDet.lines[1] or self.walls[2]):  # 
                    self.CarCon.move()
                    pass
                    #отворачиваем
            else:
                    self.CarCon.move() #прямо
        return self.TroubleDet.sign #иначе завершаем движение и выдаем знак
    
    
    def StayOnTheLine(self, joint): #двигаемся по маршруту
        while(not self.WallDet.crossroad): #проверяем что ничего нового не встретилось
            self.SemaforHandler()
            if (self.TroubleDet.signs!=0):
                self.SignHandler(self.TroubleDet.signs,joint)
            else:
                if self.LineDet.lines[0] or self.walls[0]: #отъезжаем от стены или от линии подобрать константы
                    self.CarCon.move()
                    
                    pass
                    #отворачиваем
                if self.LineDet.lines[1] or self.walls[2]:  # 
                    self.CarCon.move()
                    pass
                    #отворачиваем
                else:
                    self.CarCon.move() #прямо

        return #иначе завершаем движение и выдаем почему завершили



    '''почти все отлично но перекрестки!!'''
    def SpeedyRoad(self):# просто едем по по линии и поворачиваем на первых? поворотах направо
        
        self.WallDet.start()
        self.TroubleDet.start()
        self.LineDet.start()
        for i in range(2):#всего два поворота ведь так7
            self.SimpleLine(); #держимся нашей прямой
            if (self.TroubleDet.signs==6 or self.WallDet.crossroad or self.TroubleDet.signs==4): #поворот открылся направо
                # на самом деле достаточно знать только что правый поворот открыт но пока можно говорить что это все перекрестки
                self.TurnOn(1)
        self.TroubleDet.mark = False
        self.LineDet.mark = False
        self.WallDet.mark= False
        self.startDot=-2
        return 1  # по идее должна вернуть значение обозначающее на каком повороте мы заехали

    def CityRoad(self,startDot):

        self.WallDet.start()
        self.TroubleDet.start()
        self.LineDet.start()
        self.map = Map.MyMap(open('graph.txt')) #нам нужна карта для построения маршрута

        for joint in self.map.joints: #-2 если на втором повороте заехали, -1 если на первом для ключей
            if joint.leftDot.id==self.startDot:
                self.prev=joint
        for dot in self.map.dots:
            if dot.id==self.startDot:
                self.startDot=dot
            if dot.id==18:
                finishDot=dot
        self.Path=self.map.FindTheWay(startDot,finishDot) #теперь наш путь лежит в path
        #идея такая пытаемся поехать в нужном направлении не получилось удаляем ребро, по новой считаем
        while (startDot!=finishDot): #пока не доехали до финиша
            for joint in self.Path:
                direction=self.map.GetTurnDirection(self.prev,joint) #смотрим направление поворота на данном перекресте
                self.Car.TurnOn(direction) #поворачиваем на повороте 0 прямо 1 право -1 влево 2 круговое движение
                self.StayOnTheLine(joint) #едем и держимся линии пока ничего не мешает
                self.prev=joint #для вычисления следующего направления запоминаем ребро по которому поехали
                if (not self.WallDet.crossroad): #если что-то помешало придется вернутся и перестроить маршрут удаляя это ребро
                    #аналогично if(trouble==3) можно использовать
                    joint.Delete()
                    self.Path=self.map.FindTheWay(startDot,finishDot)
                    self.TurnOn(-2) #придется развернутся -2 разворот
                    break
                else:
                    self.startDot=joint.GetNegative(self.startDot)#если оказались на перекрестке продолжаем движение'''
        self.WallDet.mark=False
        self.TroubleDet.mark = False
        self.LineDet.mark = False
        return 2


    '''ага'''
    def CircleRoad(self):
        
        
        
        while(not self.WallDet.crossroad): #проверяем что ничего нового не встретилось
            if (self.LineDet.lines[0] or self.walls[0]): #отъезжаем от стены или от линии подобрать константы
                    self.CarCon.move()
                    pass
                    #отворачиваем
            if (self.LineDet.lines[1] or self.walls[2]):  # 
                    self.CarCon.move()
                    pass
                    #отворачиваем
            else:
                    self.CarCon.move() #прямо
        return 3



    '''тут все доделать'''
    def Parking(self):
        self.WallDet.start()
        self.LineDet.parking=True
        self.LineDet.start()
        
        while (ParkingDis меньше const): #подъезжаем
           self.CarCon.move()
        
        #паркуемся
        
        
        self.WallDet.mark=False
        self.LineDet.mark = False
        return 4





