# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 19:57:30 2018

@author: Илья
"""

import cv2
import numpy as np
from keras.models import model_from_json
from sklearn.externals import joblib
from cv2 import HOGDescriptor
from numpy.linalg import norm
#from testMethod import DetectRedSign

class Detector:
    
    def __init__(self):
        self.json_file_red = open('model_red_good.json', 'r')
        self.loaded_model_json_red = self.json_file_red.read()
        self.json_file_red.close()
        self.loaded_model_red = model_from_json(self.loaded_model_json_red)
        # load weights into new model
        self.loaded_model_red.load_weights("model_red_good.h5")
        print("Loaded red model from disk")
        
        self.json_file_blue = open('model_good_blue_3.json', 'r')
        self.loaded_model_json_blue = self.json_file_blue.read()
        self.json_file_blue.close()
        self.loaded_model_blue = model_from_json(self.loaded_model_json_blue)
        # load weights into new model
        self.loaded_model_blue.load_weights("model_good_blue_3.h5")
        print("Loaded blue model from disk")
        
        self.trLigh_clf = joblib.load('clf_tf_hog4.pkl')
        #self.trLigh_clf = joblib.load('model_semafors.pkl')
        print("Loaded tl svm model from disk")
        
        self.json_file_tl = open('model_small_tl_1.json', 'r')
        self.loaded_model_json_tl = self.json_file_tl.read()
        self.json_file_tl.close()
        self.loaded_model_tl = model_from_json(self.loaded_model_json_tl)
        # load weights into new model
        self.loaded_model_tl.load_weights("model_small_tl_1.h5")
        print("Loaded tl nn model from disk")
        
        
        
        
    def DetectRedSign(self,frame,visualize = False):
        if (frame is None):
            return 0
        
        f_height, f_width,_ = frame.shape
        f_area = f_height*f_width
        
        #noramalization
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9,9))
        frame2 = cv2.medianBlur(frame,3)      
        frame2 = cv2.GaussianBlur(frame2,(3,3),2)
        #masking
        hsv_image_1 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
            
        # lower mask (0-10)
        lower_red = np.array([0,50,50])
        upper_red = np.array([10,255,255])
        mask0 = cv2.inRange(hsv_image_1, lower_red, upper_red)
            
        # upper mask (170-180)
        lower_red = np.array([170,50,50])
        upper_red = np.array([180,255,255])
        mask1 = cv2.inRange(hsv_image_1, lower_red, upper_red)
            
        mask = cv2.bitwise_or(mask0,mask1)
        #mask = mask0+mask1
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        if (visualize):
            cv2.imshow('mask',mask)
        
        _,contours,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL,2)
        
        if len(contours) > 0:
            for cnt in contours:
                if (cv2.contourArea(cnt) > 0):
                    x,y,w,h = cv2.boundingRect(cnt)
                    x = int(x)
                    y = int(y)
                    w = int(w)
                    h = int(h)
                        
                    c_area = w*h
                    aspect_ratio = w/h    
                    if (c_area > 0 and aspect_ratio > 0.6 and aspect_ratio < 1.05):
                        if (c_area >=400): #f_area/c_area >= 50 and    messy shit
                            cut_sign_candidate = frame[y:y+w,x:x+h,:]
                            cut_sign_candidateRes = cv2.resize(cut_sign_candidate,(20, 20), interpolation = cv2.INTER_CUBIC)
                            k = self.loaded_model_red.predict(np.expand_dims(np.array(cut_sign_candidateRes.astype("float") / 255.0), axis=0))
                            
                            red_prob = k[0][0]*100
                            if (red_prob>85):
                                if (visualize):
                                    cv2.rectangle(frame, (x,y),(x+w,y+h),(0,0,255),2) #red
                                    cv2.putText(frame, "{}:{}%".format('S',int(red_prob)),
                                                 (x, int(y - 15)),
                                                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,255), 2)
                                return 1
                            else:
                                #отсечечка по нейросетки красные знаки
                                if (visualize):
                                    cv2.rectangle(frame, (x,y),(x+w,y+h),(0,125,255),2) #orange
                                    cv2.putText(frame, "{}:{}%".format('S',int(red_prob)),
                                                 (x, int(y - 15)),
                                                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,125,255), 2)
                    else:
                        #отсечечка по размеру красные знаки
                        if (visualize):
                            cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,255),2) #yellow
                            
          
        return 0
        
    def DetectBlueSign(self,frame,visualize = False):
        if (frame is None):
            return 0
        
        f_height, f_width,_ = frame.shape
        f_area = f_height*f_width
        
        #noramalization
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9,9))
        frame2 = cv2.medianBlur(frame,3)      
        frame2 = cv2.GaussianBlur(frame2,(3,3),2)
        #masking
        hsv_image_1 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
        low_blue = (105,120,50)
        high_blue = (120,255,255)
        mask = cv2.inRange(hsv_image_1, low_blue, high_blue)  
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        if (visualize):
            cv2.imshow('mask',mask)
        
        _,contours,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL,2)
        
        if len(contours) > 0:
            for cnt in contours:
                if (cv2.contourArea(cnt) > 0):
                    x,y,w,h = cv2.boundingRect(cnt)
                    x = int(x)
                    y = int(y)
                    w = int(w)
                    h = int(h)
                        
                    c_area = w*h
                    aspect_ratio = w/h    
                    if (visualize):
                        print(c_area)
                    
                    if (c_area > 0 and aspect_ratio > 0.5 and aspect_ratio < 1.5): # 
                        if (c_area >=400): #messy shit #f_area/c_area >= 50 and 
                            
                            cut_sign_candidate = frame[y:y+w,x:x+h,:]
                            cut_sign_candidateRes = cv2.resize(cut_sign_candidate,(20, 20), interpolation = cv2.INTER_CUBIC)
                            k = self.loaded_model_blue.predict(np.expand_dims(np.array(cut_sign_candidateRes.astype("float") / 255.0), axis=0))
                            
                            max_prob_index = np.argmax(k[0])
                            blue_prob = k[0][max_prob_index]*100
                            
                            if (blue_prob>85):
                                classId = 8
                                className = 'NS'
                                
                                if (max_prob_index == 0):
                                    classId = 3
                                    className = 'F'
                                elif (max_prob_index == 1):
                                    classId = 4
                                    className = 'R'
                                elif (max_prob_index == 2):
                                    classId = 5
                                    className = 'L'
                                elif (max_prob_index == 3):
                                    classId = 6
                                    className = 'FR'
                                elif (max_prob_index == 4):
                                    classId = 7
                                    className = 'FL'
                                else:
                                    classId = 8 
                                
                                if (visualize):
                                    cv2.rectangle(frame, (x,y),(x+w,y+h),(255,0,0),2) #blue
                                    cv2.putText(frame, "{}:{}%".format(className,int(blue_prob)),
                                                 (x, int(y - 15)),
                                                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
                                return classId
                            else:
                                #отсечечка по нейросетки синие знаки
                                if (visualize):
                                    cv2.rectangle(frame, (x,y),(x+w,y+h),(255,0,255),2) #violet
                                    cv2.putText(frame, "{}:{}%".format('NS',int(blue_prob)),
                                                 (x, int(y - 15)),
                                                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,0,255), 2)
                    else:
                        #отсечечка по размеру синие знаки
                        if (visualize):
                            cv2.rectangle(frame, (x,y),(x+w,y+h),(255,255,0),2) #lightblue
                                         
        return 8
    
    def cmptFeatures(self,image):
        winSize = (16,48)
        blockSize = (16,16)
        blockStride = (8,8)
        cellSize = (8,8)
        nbins = 9
        derivAperture = 1
        winSigma = 4.
        histogramNormType = 0
        L2HysThreshold = 2.0000000000000001e-01
        gammaCorrection = 100
        nlevels = 32
        hog = HOGDescriptor(winSize,blockSize,blockStride,cellSize,nbins,derivAperture,winSigma,
                            histogramNormType,L2HysThreshold,gammaCorrection,nlevels)
        winStride = (8,8)
        padding = (16,16)
        hist = hog.compute(image,winStride,padding)
        return np.reshape(hist, 4500)
    
    def hog(self,img,step):
        gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
        mag, ang = cv2.cartToPolar(gx, gy)
        bin_n = 16 # Number of bins
        bin = np.int32(bin_n*ang/(2*np.pi))
    
        bin_cells = []
        mag_cells = []
    
        cellx = celly = step
        
        for i in range(0,int(img.shape[0]/celly)):
            for j in range(0,int(img.shape[1]/cellx)):
                bin_cells.append(bin[i*celly : i*celly+celly, j*cellx : j*cellx+cellx])
                mag_cells.append(mag[i*celly : i*celly+celly, j*cellx : j*cellx+cellx])   
    
        hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
        hist = np.hstack(hists)
    
        # transform to Hellinger kernel
        eps = 1e-7
        hist /= hist.sum() + eps
        hist = np.sqrt(hist)
        hist /= norm(hist) + eps
        return hist
    
    def getHOGFeatures(self,X,step):
        return [self.hog(x,step) for x in X]
    
    def DetectTrLight(self,frame,visualize=True):
        #frame = cv2.resize(frame,(640, 360), interpolation = cv2.INTER_CUBIC)
        low_red = (0,0,200)
        hight_red = (140,140,255)
        mask = cv2.inRange(frame, low_red, hight_red)
        cont = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)[1]
        for cnt in cont:
            moments = cv2.moments(cnt, 255)
            dM01 = moments['m01']
            dM10 = moments['m10']
            dArea = moments['m00']
            if dArea > 30:                #Отбрасывание контуров по площади
                x = int(dM10 / dArea) # x координата центра масс контура
                y = int(dM01 / dArea) # у координата цента масс контура
                #L,R,T,B - кайние точки контура, левая, правая, верхняя, нижняя соответственно
                L = tuple(cnt[cnt[:, :, 0].argmin()][0])
                R = tuple(cnt[cnt[:, :, 0].argmax()][0])
                T = tuple(cnt[cnt[:, :, 1].argmin()][0])
                B = tuple(cnt[cnt[:, :, 1].argmax()][0])
                diam1 = R[0] - L[0]
                diam2 = B[1] - T[1]
                r = int((diam1+diam2)/4) # средний радиус контура
                if(y > 3*r and x > 3*r and diam1/diam2 > 0.85 and diam1/diam2 < 1.15): # первые 2 условия для корректного вырезания контура
                    cut_frame = []
                    if r < 5: # С этими условиями результат получается лучше
                        cut_frame = frame[(y-r*3):(y+r*9),(x-r*3):(x+r*3)]
                    else:
                        cut_frame = frame[(y-r*2):(y+r*7),(x-r*2):(x+r*2)]
                    cut_frame = cv2.resize(cut_frame,(20, 60), interpolation = cv2.INTER_CUBIC)
                    
                    features = self.getHOGFeatures([cut_frame],4)
                    print(features)
                    pred = self.trLigh_clf.predict_proba(features)[0][1]
                    pred = pred*100
                    if(pred>70):
                        if (visualize):
                            cv2.rectangle(frame,(x-r*3,y-r*3),(x+r*3,y+r*8),(0,255,0),2)
                            cv2.putText(frame, "{}:{}%".format('TL',int(pred)),
                                                 (x, int(y - 15)),
                                                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,255,0), 2)
                    
                        return 1
                    else:
                        if (visualize):
                            cv2.rectangle(frame,(x-r*3,y-r*3),(x+r*3,y+r*8),(128,128,128),2)
                            cv2.putText(frame, "{}:{}%".format('TL',int(pred)),
                                                 (x, int(y - 15)),
                                                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (128,128,128), 2)
                else:
                    if (visualize):
                            cv2.rectangle(frame,(x-r*3,y-r*3),(x+r*3,y+r*8),(0,0,0),2)
        return 0

    def DetectTrLightNN(self,frame,visualize=True):
        #frame = cv2.resize(frame,(640, 360), interpolation = cv2.INTER_CUBIC)
        low_red = (0,0,200)
        hight_red = (140,140,255)
        mask = cv2.inRange(frame, low_red, hight_red)
        cont = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)[1]
        for cnt in cont:
            moments = cv2.moments(cnt, 255)
            dM01 = moments['m01']
            dM10 = moments['m10']
            dArea = moments['m00']
            if dArea > 30:                #Отбрасывание контуров по площади
                x = int(dM10 / dArea) # x координата центра масс контура
                y = int(dM01 / dArea) # у координата цента масс контура
                #L,R,T,B - кайние точки контура, левая, правая, верхняя, нижняя соответственно
                L = tuple(cnt[cnt[:, :, 0].argmin()][0])
                R = tuple(cnt[cnt[:, :, 0].argmax()][0])
                T = tuple(cnt[cnt[:, :, 1].argmin()][0])
                B = tuple(cnt[cnt[:, :, 1].argmax()][0])
                diam1 = R[0] - L[0]
                diam2 = B[1] - T[1]
                r = int((diam1+diam2)/4) # средний радиус контура
                if(y > 3*r and x > 3*r and diam1/diam2 > 0.85 and diam1/diam2 < 1.15): # первые 2 условия для корректного вырезания контура
                    cut_frame = []
                    if r < 5: # С этими условиями результат получается лучше
                        cut_frame = frame[(y-r*3):(y+r*9),(x-r*3):(x+r*3)]
                    else:
                        cut_frame = frame[(y-r*2):(y+r*7),(x-r*2):(x+r*2)]
                    
                    cut_frame = cv2.resize(cut_frame,(20, 60), interpolation = cv2.INTER_CUBIC)
                    k = self.loaded_model_tl.predict(np.expand_dims(np.array(cut_frame.astype("float") / 255.0), axis=0))
                            
                    tl_prob = k[0][0]*100
                    if(tl_prob>70):
                        if (visualize):
                            cv2.rectangle(frame,(x-r*3,y-r*3),(x+r*3,y+r*8),(0,255,0),2)
                            cv2.putText(frame, "{}:{}%".format('TL',int(tl_prob)),
                                                 (x, int(y - 15)),
                                                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,255,0), 2)
                    
                        return 1
                    else:
                        if (visualize):
                            cv2.rectangle(frame,(x-r*3,y-r*3),(x+r*3,y+r*8),(128,128,128),2)
                            cv2.putText(frame, "{}:{}%".format('TL',int(tl_prob)),
                                                 (x, int(y - 15)),
                                                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (128,128,128), 2)
                else:
                    if (visualize):
                            cv2.rectangle(frame,(x-r*3,y-r*3),(x+r*3,y+r*8),(0,0,0),2)
        return 0

    def DetectTrLightNN2(self,frame,visualize=True):
        if (frame is None):
            return 0
        
        f_height, f_width,_ = frame.shape
        f_area = f_height*f_width
        
        #noramalization
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9,9))
        frame2 = cv2.medianBlur(frame,3)      
        frame2 = cv2.GaussianBlur(frame2,(3,3),2)
        
        useTLRed = 1
        
        if (useTLRed == 1):
            #masking
            hsv_image_1 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
            # lower mask (0-10)
            lower_red = np.array([0,50,50])
            upper_red = np.array([10,255,255])
            mask0 = cv2.inRange(hsv_image_1, lower_red, upper_red)
                
            # upper mask (170-180)
            lower_red = np.array([170,50,50])
            upper_red = np.array([180,255,255])
            mask1 = cv2.inRange(hsv_image_1, lower_red, upper_red)
                
            mask = cv2.bitwise_or(mask0,mask1)
            #mask = mask0+mask1
        else:
            low_red = (0,0,200)
            hight_red = (140,140,255)
            mask = cv2.inRange(frame, low_red, hight_red)
        
        if (visualize):
            cv2.imshow('tl mask', mask)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        _,contours,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL,2)
        
        if len(contours) > 0:
            for cnt in contours:
                
                x,y,w,h = cv2.boundingRect(cnt)
                x = int(x)
                y = int(y)
                w = int(w)
                h = int(h)
                if (cv2.contourArea(cnt) > 0):
                    c_area = w*h
                    aspect_ratio = w/h
                    
                    y_min = y
                    y_max = y + 3*h
                    x_min = x
                    x_max = x + w
                            
                    if (c_area > 0 and aspect_ratio > 0.6 and aspect_ratio < 1.5):
                        if (f_area/c_area >= 50 and c_area >=400): #messy shit
                            
                            cut_tl_candidate = frame[y_min:y_max,x_min:x_max,:]
                            cut_tl_candidateRes = cv2.resize(cut_tl_candidate,(20, 60), interpolation = cv2.INTER_CUBIC)
                                
                            k = self.loaded_model_tl.predict(np.expand_dims(np.array(cut_tl_candidateRes.astype("float") / 255.0), axis=0))
                            tl_prob = k[0][1]*100
                            
                            features = self.getHOGFeatures([cut_tl_candidateRes],4)
                            pred = self.trLigh_clf.predict_proba(features)[0][1]
                            pred = pred*100
                            
                            print('{};{}'.format(tl_prob,pred))
                            
                            if(tl_prob>70):
                                if (visualize):
                                    cv2.rectangle(frame,(x_min,y_min),(x_max,y_max),(0,255,0),2)
                                    cv2.putText(frame, "{}:{}%".format('TL',int(tl_prob)),
                                                    (x, int(y - 15)),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,255,0), 2)
                        
                                return 1
                            else:
                                if (visualize):
                                    cv2.rectangle(frame,(x_min,y_min),(x_max,y_max),(128,128,128),2)
                                    cv2.putText(frame, "{}:{}%".format('TL',int(tl_prob)),
                                                    (x, int(y - 15)),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (128,128,128), 2)
                    else:
                        if (visualize):
                            cv2.rectangle(frame,(x_min,y_min),(x_max,y_max),(0,0,0),2)
        return 0