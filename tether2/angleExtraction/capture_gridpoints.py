"""A module to generate the camera calibration file for a specific AlbatrossOne Test

take input argumets of a video file and assiasted frame. the user will then be prompted to select all the
internal corners of a checkerboard. the user must start form the top left corner and select all the points
row by row, working down.
"""
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

ap = argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("-v", "--video", required = True, help = "Video To pass")
ap.add_argument("-f", "--frame",type=int, default = 0, help = "Frame to calibrate at")
ap.add_argument("-r","--roi", nargs="+", type=int,help="list of 4 values defining ROI, if not provided user will be prompt to select one")
ap.add_argument("-x","--nx", required = True, type=int,help="number of inner corners in x direction")
ap.add_argument("-y","--ny", required = True, type=int,help="number of inner corners in y direction")
ap.add_argument("-o","--output_file",help="Output file location")
args = vars(ap.parse_args())

print('Loading Frame')
# get reqired frame
cap = cv2.VideoCapture(args['video'])
cap.set(cv2.CAP_PROP_POS_FRAMES, args['frame'])
ret,frame = cap.read()
if not ret:
    raise ValueError("could not successful retrieve video frame")

# Select ROI to perform analysis in
if args['roi'] is None:
    frameROI = selectROIResized('Select ROI',frame,700)
else:
    frameROI = tuple(args['roi'])
print(frameROI)
frame = crop_image(frame,frameROI)
grayColor = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
print(frame.shape[1:])

# create function for mouse click events
points = []
start = 0
def mouse_click(event,x,y,flags,param):
    global points,start
    if event == cv2.EVENT_LBUTTONDOWN:
        start = timer()
    elif event == cv2.EVENT_LBUTTONUP:
        if (timer() - start)<0.2:
            points.append((x,y))

# select the grid points
cv2.namedWindow("frame")
cv2.setMouseCallback("frame", mouse_click)
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord("c"):
        break
    if key == ord("d"):
        if len(points)>0:
            points.pop()
    tmp_frame = frame.copy()    
    for p in points:
        tmp_frame[p[1],p[0]] = [0,0,255]     
    cv2.putText(tmp_frame,f"FC? {ret}",(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0,2)) 
    cv2.imshow('frame',tmp_frame)

initial_points = np.array(points)

# refine the grid point selectons
# define the criteria to stop and refine the corners
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
corners = cv2.cornerSubPix(grayColor,np.float32(initial_points),(5,5),(-1,-1),criteria)

# Plot the refined points
res = np.hstack((initial_points,corners))
res = np.int0(res)
frame[res[:,1],res[:,0]]= [0,0,255]
frame[res[:,3],res[:,2]] = [0,255,0]
cv2.imshow('frame',frame)
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord("c"):
        break

# Plot the chessboard 
objp = np.zeros((args['nx']*args['ny'],3), np.float32)
objp[:,:2] =  np.mgrid[0:args['nx'],0:args['ny']].T.reshape(-1,2) # x,y coordinates
cb = cv2.drawChessboardCorners(frame.copy(), (args['nx'], args['ny']), corners, True)
cv2.imshow('frame',cb)
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord("c"):
        break

# show the undistored and distroted image side by side
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera([objp], [corners], frame.shape[1:], None, None)
undist = cv2.undistort(frame.copy(), mtx, dist, None, mtx)
cv2.imshow('frame',np.hstack((frame,undist)))
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord("c"):
        break


# When everything done, release the video capture object and close all frames
cap.release()
cv2.destroyAllWindows()

# save the data as a pickle file
pickle.dump({"threedpoints":objp,"twodpoints":corners,
            "nx":args["nx"],"ny":args["ny"],
            "roi":frameROI},
            open(args['output_file'],"wb"))