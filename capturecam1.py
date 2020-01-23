#imports
import cv2, time
import numpy
import math
from enum import Enum
import random as rng
from networktables import NetworkTables
rng.seed(12345)
#NetworkTables.initialize(server='10.22.83.2')
NetworkTables.startClientTeam(2283)
table = NetworkTables.getDefault().getTable('SmartDashboard')

#global variables
frame = None
frame1 = None
frame2 = None
frame3 = None
frame4 = None
frame5 = None
frame6 = None
frame7 = None
contours1 = None
contours2 = None
center_coordinates = (320, 230)

blur_ksize=7

hue = [51,84]
sat = [50,230]
val = [55,134]

kernel = None
anchor = (-1, -1)
iterations = 3.0
border_type = cv2.BORDER_CONSTANT
border_value = (-1)


external_only = False
#im2 = None

min_area = 0
min_perimeter = 0
min_width = 0
max_width = 1000
min_height = 0
max_height = 1000
solidity = [75, 75]
max_vertices = 1000000
min_vertices = 0
min_ratio = 0
max_ratio = 1000
output = None

#color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
color = (0,0,255)
color1 = (0,255,0)
fcolor = (0,0,255)

font = cv2.FONT_HERSHEY_PLAIN

thickness = 2
fontScale = 1

video=cv2.VideoCapture(0)

#functions
def _blur(image):
    return cv2.blur(image, (blur_ksize, blur_ksize))

def _HSV_Threshold(image):
    out = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
    return cv2.inRange(out, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))

def _dilate(image):
        
        return cv2.dilate(frame2, kernel, anchor, iterations = (int) (iterations +0.5),
                            borderType = border_type, borderValue = border_value)

def _erode(image):
        
        return cv2.erode(frame3, kernel, anchor, iterations = (int) (iterations +0.5),
                            borderType = border_type, borderValue = border_value)

def _erode2(image):

        return cv2.erode(frame4, kernel, anchor, iterations = (int) (iterations +0.5),
                            borderType = border_type, borderValue = border_value)

def _dialate2(image):

       return cv2.dilate(frame5, kernel, anchor, iterations = (int) (iterations +0.5),
                            borderType = border_type, borderValue = border_value)

def _find_contours(image):
    if(external_only):
            mode = cv2.RETR_EXTERNAL
    else:
        mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        contours1,_ = cv2.findContours(frame6, mode=mode, method=method)
        
        return contours1

def _filter_contours(contours1):
    output = []
    for contour in contours1:
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        solid = 100 * area / cv2.contourArea(hull)
        if  (solid < solidity[0] or solid > solidity[1]):
            return contour
        
while (True):
    check, frame = video.read()
    frame1 = _blur(frame)
    frame2 = _HSV_Threshold(frame1)
    frame3 = _dilate(frame2)
    frame4 = _erode(frame3)
    frame5 = _erode2(frame4)
    frame6 = _dialate2(frame5)
    cv2.circle(frame, center_coordinates, 4, fcolor, 2)
    
    contours1 = _find_contours(frame6)
    contours2 = _filter_contours(contours1)
    contours_poly = [None]*len(contours1)
    boundRect = [None]*len(contours1)
    centers = [None]*len(contours1)
    radius = [None]*len(contours1)
    
    for i, c in enumerate(contours1):
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        boundRect[i] = cv2.boundingRect(contours_poly[i])
        centers[i], radius[i] = cv2.minEnclosingCircle(contours_poly[i])
       

    for i in range(len(contours1)):
        '''
        cv2.rectangle(frame, (int(boundRect[i][0]), int(boundRect[i][1])), (int(boundRect[i][0]+boundRect[i][2]), int(boundRect[i][1]+boundRect[i][3])), color, 2)
        cv2.circle(frame, (int(centers[i][0]), int(centers[i][1])), int(radius[i]), color1, 2)
        cv2.circle(frame, (int(centers[i][0]), int(centers[i][1])), 2, color1, 4)'''
        
        
        table.putString('DB/String 0', "Eje X: " + str(centers[i][0]))
        table.putString('DB/String 1', "Eje Y: " + str(centers[i][1]))
        table.putNumber('DB/Slider 0', centers[i][0])
        table.putNumber('DB/Slider 1', centers[i][1])
        
        

        

    frame7 =  cv2.drawContours(frame, contours1, -1, (255,100,0), 3)
    
    
     
   
    

    #cv2.imshow('Feed', frame7)
    if cv2.waitKey(1) & 0xFF == ord('f'):
        break
      
video.release()

#poner esto en la consola:  LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 capturecam.py
