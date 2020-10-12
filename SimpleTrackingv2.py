import numpy as np 
import cv2
import os
import sys
import argparse
import matplotlib.pyplot as plt
import torch

def cropImage(img,bb):
    return img[bb[1]:bb[1]+bb[3],bb[0]:bb[0]+bb[2]]


ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required = True, help = "Video To pass")
ap.add_argument("-t", "--tracker", type=str, default="kcf",
	help="OpenCV object tracker type")
args = vars(ap.parse_args())

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}
# grab the appropriate object tracker using our dictionary of
# OpenCV object tracker objects
trackers = cv2.MultiTracker_create()

print('Loading Video')


# Select ROI to perform analysis in
cap = cv2.VideoCapture(args['video'])
ret,frame = cap.read()
ROIs = cv2.selectROIs('Select ROIs', frame, False)
frameROI = ROIs[0].copy()


# Select Tracking object
roi = cropImage(frame,frameROI)
roi = cv2.resize(roi, (0,0), fx=2, fy=2) 
roi = cv2.GaussianBlur(roi,(3,3),0)
#roi = cv2.Canny(roi,100,255)

ROI = cv2.selectROI('Select ROIs', roi, False)
tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
trackers.add(tracker, roi, ROI)

ROI = cv2.selectROI('Select ROIs', roi, False)
tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
trackers.add(tracker, roi, ROI)




tracker.init(roi,ROI)

def drawBox(img,bb):
    x,y,w,h = (int(b) for b in bb)
    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,100),3,1)
    return img

frame_val = 1
while True:
    key = cv2.waitKey(10) & 0xFF
    if key == ord("c"):
        break
    ret,frame = cap.read()
    roi = cropImage(frame,frameROI)
    roi = cv2.resize(roi, (0,0), fx=2, fy=2) 
    roi = cv2.GaussianBlur(roi,(3,3),0)
    #roi = cv2.Canny(roi,100,255)
    (success, boxes) = trackers.update(roi)
    if success:
        for box in boxes:
            roi = drawBox(roi,box)
        cv2.putText(roi,"Tracking",(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0,2))
    else:
        cv2.putText(roi,"Lost",(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255,2)) 
    cv2.imshow('frame',roi)

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()








