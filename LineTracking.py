import numpy as np 
import cv2
import os
import sys
import argparse
import matplotlib.pyplot as plt
import torch
from image_ultilites import selectROIResized,undistort_image

def cropImage(img,bb):
    return img[bb[1]:bb[1]+bb[3],bb[0]:bb[0]+bb[2]]

distCoeff = np.zeros((4,1),np.float64)

# TODO: add your coefficients here!
k1 = 0.0 # negative to remove barrel distortion
k2 = 0.0
p1 = 0.0
p2 = 0.0

# assume unit matrix for camera
cam = np.eye(3,dtype=np.float32)


ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required = True, help = "Video To pass")
args = vars(ap.parse_args())

print('Loading Video')

# Select ROI to perform analysis in
cap = cv2.VideoCapture(args['video'])
ret,frame = cap.read()
# frame = undistort_image(frame,1150,(k1,k2,p1,p2))
ROI = selectROIResized('Select ROI',frame,800)
frameROI = ROI

while True:
    key = cv2.waitKey(10) & 0xFF
    if key == ord("c"):
        break
    ret,frame = cap.read()
    width  = frame.shape[1]
    height = frame.shape[0]
    #frame = cv2.undistort(frame,cam,distCoeff)
    roi = cropImage(frame,frameROI)
    roi = cv2.resize(roi, (0,0), fx=2, fy=2) 
    roi = cv2.GaussianBlur(roi,(5,5),0)
    edges = cv2.Canny(roi,50,255)
    lines = cv2.HoughLines(edges,1,np.pi/180, 5)
    if lines is not None:
        for r,theta in lines[0]:
            # Stores the value of cos(theta) in a 
            a = np.cos(theta) 
        
            # Stores the value of sin(theta) in b 
            b = np.sin(theta) 
            
            # x0 stores the value rcos(theta) 
            x0 = a*r 
            
            # y0 stores the value rsin(theta) 
            y0 = b*r 
            
            # x1 stores the rounded off value of (rcos(theta)-1000sin(theta)) 
            x1 = int(x0 + 1000*(-b)) 
            
            # y1 stores the rounded off value of (rsin(theta)+1000cos(theta)) 
            y1 = int(y0 + 1000*(a)) 
        
            # x2 stores the rounded off value of (rcos(theta)+1000sin(theta)) 
            x2 = int(x0 - 1000*(-b)) 
            
            # y2 stores the rounded off value of (rsin(theta)-1000cos(theta)) 
            y2 = int(y0 - 1000*(a)) 
            
            # cv2.line draws a line in img from the point(x1,y1) to (x2,y2). 
            # (0,0,255) denotes the colour of the line to be  
            #drawn. In this case, it is red.  
            roi = cv2.line(roi,(x1,y1), (x2,y2), (0,0,255),2) 
    cv2.imshow('frame',roi)

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()








