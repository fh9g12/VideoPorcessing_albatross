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
ap.add_argument("-r","--roi", nargs="+", type=int)
args = vars(ap.parse_args())
print(args['roi'])
print('Loading Video')
# Select ROI to perform analysis in
cap = cv2.VideoCapture(args['video'])

frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"FPS: {fps}")
print(f"Frame Count: {frame_count}")
cap.set(cv2.CAP_PROP_POS_FRAMES, args['start_frame'])
ret,frame = cap.read()

if args['roi'] is None:
    frameROI = selectROIResized('Select ROI',frame,700)
else:
    frameROI = tuple(args['roi'])
frame = crop_image(frame,frameROI)
#filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
#frame=cv2.filter2D(frame,-1,filter)
print(frameROI)

# Define the dimensions of checkerboard 
CHECKERBOARD = (9, 14) 
  
  
# stop the iteration when specified 
# accuracy, epsilon, is reached or 
# specified number of iterations are completed. 
criteria = (cv2.TERM_CRITERIA_EPS + 
            cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001) 
  
  
# Vector for 3D points 
threedpoints = [] 
  
# Vector for 2D points 
twodpoints = [] 
  
  
#  3D points real world coordinates 
objectp3d = np.zeros((1, CHECKERBOARD[0]  
                      * CHECKERBOARD[1],  
                      3), np.float32) 
objectp3d[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 
                               0:CHECKERBOARD[1]].T.reshape(-1, 2) 
prev_img_shape = None

grayColor = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

cv2.namedWindow("frame")
cv2.setMouseCallback("frame", mouse_click)

while True:
    key = cv2.waitKey(10) & 0xFF
    if key == ord("c"):
        break
    tmp_frame = frame.copy()    
    cv2.putText(tmp_frame,f"FC? {ret}",(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0,2)) 
    cv2.imshow('frame',tmp_frame)

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()