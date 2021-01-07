import numpy as np 
import cv2
import os, sys
import argparse
import pandas as pd
import pickle
from timeit import default_timer as timer
from tqdm.auto import tqdm

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.append(parentdir)
from image_ultilites import crop_image,selectROIResized


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

x_click = 0
y_click = 0

def mouse_click(event,x,y,flags,param):
    global x_click,y_click
    if event == cv2.EVENT_LBUTTONDOWN:
        x_click = x
        y_click = y


ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required = True, help = "Video To pass")
ap.add_argument("-s", "--start_frame",type=int, default = 0, help = "Frame to start at")
args = vars(ap.parse_args())

print('Loading Video')
# Select ROI to perform analysis in
cap = cv2.VideoCapture(args['video'])

frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"FPS: {fps}")
print(f"Frame Count: {frame_count}")
cap.set(cv2.CAP_PROP_POS_FRAMES, args['start_frame'])
ret,frame = cap.read()

frame_pos = args['start_frame']
pause = True
rate = 1

cv2.namedWindow("frame",cv2.WINDOW_GUI_EXPANDED)
#cv2.setMouseCallback("frame", mouse_click)

while frame_pos < frame_count:
    key = cv2.waitKey(1) & 0xFF
    if key == ord(" "):
        pause = not pause
    if key == ord("s"):
        if pause:
            ret,frame = cap.read()
            frame_pos += 1
    if key == ord("f"):
        break
    if key == ord("1"):
        rate = 1
    if key == ord("2"):
        rate = 4
    if key == ord("3"):
        rate = 6
    if key == ord("4"):
        rate = 12
    if key == ord("5"):
        rate = 24
    if not pause:
        for i in range(rate):
            ret,frame = cap.read()
            frame_pos += 1
    tmp_frame = frame.copy()      
    cv2.putText(tmp_frame,f"Frame: {frame_pos}",(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0,2))
    cv2.putText(tmp_frame,f"x: {x_click:.2f}, y: {y_click:.2f}",(50,100),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0,2)) 
    cv2.imshow('frame',tmp_frame)

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()