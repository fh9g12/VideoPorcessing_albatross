import numpy as np 
import cv2
import os
import sys
import argparse
import matplotlib.pyplot as plt
import torch

def cropImage(img,boundingbox):
    return img[boundingbox[1]:boundingbox[1]+boundingbox[3],boundingbox[0]:boundingbox[0]+boundingbox[2]]

def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required = True, help = "Video To pass")
args = vars(ap.parse_args())


print('Loading Video')


# Select ROI to perform analysis in
cap = cv2.VideoCapture('/Users/fintan/PhD Files/Data/AlbatrossOneData/06_2020/FLT2.2_flying.mp4')
ret,frame = cap.read()
ROIs = cv2.selectROIs('Select ROIs', frame, False)
frameROI = ROIs[0].copy()


# Select Template
roi = cropImage(frame,frameROI)
roi = cv2.GaussianBlur(roi,(5,5),0)
ROIs = cv2.selectROIs('Select ROIs', roi, False)

template = cropImage(roi,ROIs[0])


frame_val = 1
while True:
    ret,frame = cap.read()
    frame_val = frame_val+1
    if frame_val%100==0:
        angles = np.linspace(-45,45,181)
        res = []
        roi = cropImage(frame,frameROI)
        roi = cv2.GaussianBlur(roi,(5,5),0)
        for idx, val in enumerate(angles):
            img_rot = rotate_bound(template,val)
            resmap = cv2.matchTemplate(roi,img_rot,cv2.TM_SQDIFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resmap)
            res.append((min_val,max_val,min_loc[0],min_loc[1],max_loc[0],max_loc[1],val))
        res = np.array(res)
        min_idx = np.argmin(res[:,1])
        print(res[min_idx,6])
        cv2.imshow('frame',frame)
        cv2.waitKey()


# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()








