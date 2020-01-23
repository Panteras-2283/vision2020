#imports
import cv2, time
import threading
import numpy
import math
from enum import Enum
import random as rng
from networktables import NetworkTables
import datetime
from datetime import timedelta
rng.seed(12345)
#NetworkTables.initialize(server='10.22.83.2')
NetworkTables.startClientTeam(2283)
table = NetworkTables.getDefault().getTable('SmartDashboard')

#global variables

center_coordinates = (320, 230)

blur_ksize=7

hue = [65,80]
sat = [85,255]
val = [40,255]

kernel = None
anchor = (-1, -1)
iterations = 3.0
border_type = cv2.BORDER_CONSTANT
border_value = (-1)




'''min_area = 0
min_perimeter = 0
min_width = 0
max_width = 1000
min_height = 0
max_height = 1000 '''
solidity = [7, 90]
'''max_vertices = 1000000
min_vertices = 0
min_ratio = 0
max_ratio = 1000
output = None'''

#color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
color = (0,0,255)
color1 = (0,255,0)
fcolor = (0,0,255)

font = cv2.FONT_HERSHEY_PLAIN
thickness = 2
fontScale = 1

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
cap.set(cv2.CAP_PROP_EXPOSURE, 3)

target_found = False


#functions
def _blur(image):
    return cv2.blur(image, (blur_ksize, blur_ksize))

def _HSV_Threshold(image):
    out = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return cv2.inRange(out, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))

def _dilate(image):
        
        return cv2.dilate(image, kernel, anchor, iterations = (int) (iterations +0.5),
                            borderType = border_type, borderValue = border_value)

def _erode(image):
        
        return cv2.erode(image, kernel, anchor, iterations = (int) (iterations +0.5),
                            borderType = border_type, borderValue = border_value)
def _find_contours(image):
    
    mode = cv2.RETR_LIST
    method = cv2.CHAIN_APPROX_SIMPLE
    contours,_ = cv2.findContours(image, mode=mode, method=method)
    return contours

def _filter_contours(contours):
    output = []
    solid = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        solid = 100 * area / cv2.contourArea(hull)
        if  (solid > solidity[0] or solid < solidity[1]):
             output.append(contour)
    return (output, solid)
        
def _filters(original_frame):
    #check, original_frame = cap.read()
    frame = _blur(original_frame)
    frame = _HSV_Threshold(frame)
    frame = _dilate(frame)
    frame = _erode(frame)
    frame = _erode(frame)
    frame = _dilate(frame)
    cv2.circle(original_frame, center_coordinates, 4, fcolor, 2)
    return frame
def _ffcontours():  
    framebeta= _filters(original_frame)
    contours = []
    contours = _find_contours(framebeta)
    contours, solid = _filter_contours(contours)
    solid_text = str(solid)
    cv2.putText(original_frame , solid_text, (450,450), font, 1, fcolor, 2, cv2.LINE_AA)
    
    if len(contours) > 0:
        target = contours[0]
        target_found = True
           

        contours_poly = cv2.approxPolyDP(target, 3, True)
        boundRect = cv2.boundingRect(contours_poly)
        center, radius = cv2.minEnclosingCircle(contours_poly)
       
        
        cv2.rectangle(original_frame, (int(boundRect[0]), int(boundRect[1])), (int(boundRect[0]+boundRect[2]), int(boundRect[1]+boundRect[3])), color, 2)
        cv2.circle(original_frame, (int(center[0]), int(center[1])), int(radius), color1, 2)
        cv2.circle(original_frame, (int(center[0]), int(center[1])), 2, color1, 4)
        
        
        table.putString('DB/String 0', "Eje X: " + str(center[0] - 320))
        table.putString('DB/String 1', "Eje Y: " + str(center[1] - 230))
        table.putNumber('DB/Slider 0', center[0] - 320)
        table.putNumber('DB/Slider 1', center[1] - 230)
        
        frame =  cv2.drawContours(original_frame, contours, -1, (255,100,0), 3)
        
    else:
        target_found = False
        
    table.putBoolean('DB/LED 0', target_found)
    
    
    
     
   
while(True):   
    check, original_frame = cap.read()
#     uncomment if you want to show the window
    t1= threading.Thread(target= _filters, args= (original_frame, ) )
    
    t2= threading.Thread(target= _ffcontours, args=() )

    t1.start()
    t2.start()

    t1.join()
    t2.join()
    cv2.imshow('Feed', original_frame)

    if cv2.waitKey(1) & 0xFF == ord('f'):
     break
      
cap.release()

#poner esto en la consola:  LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 capturecam.py
