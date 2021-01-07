"""A module to generate the angle calibration for a AlbatrossOne Test"""
import numpy as np 
import cv2
import os,sys
import argparse
import pickle
from timeit import default_timer as timer

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
ap.add_argument("-f", "--frames", type=int, nargs="+", help = "Frames to calibrate at")
ap.add_argument("-a", "--angles", type=float, nargs="+", help="angle of wing in each frame")
ap.add_argument("-c","--calib_file", required=True, help="camera calibration file")
ap.add_argument("-o","--output_file",help="Output file location")
args = vars(ap.parse_args())

print('Loading Video')
# get reqired frame
cap = cv2.VideoCapture(args['video'])
# load the calibration file
calib = pickle.load(open(args["calib_file"],'rb'))
# generate camera calibration matrix
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera([calib["threedpoints"]], [calib["twodpoints"]], tuple(calib['roi'][i] for i in [2,3]), None, None)

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

#calc angle on each frame
calib_angles = args["angles"]
actual_angles = []
for f in args["frames"]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, f)
    ret,frame = cap.read()
    if not ret:
        raise ValueError("could not successful retrieve video frame")
    frame = crop_image(frame,calib["roi"])
    undist = cv2.undistort(frame.copy(), mtx, dist, None, mtx)
    grayColor = cv2.cvtColor(undist, cv2.COLOR_BGR2GRAY)

    # select the grid points
    cv2.namedWindow("frame",cv2.WINDOW_KEEPRATIO)
    cv2.setMouseCallback("frame", mouse_click)
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):
            break
        if key == ord("d"):
            if len(points)>0:
                points.pop()
        tmp_frame = undist.copy()    
        for p in points:
            tmp_frame[p[1],p[0]] = [0,0,255]     
        cv2.imshow('frame',tmp_frame)
    deltas = [x[0]-x[1] for x in (zip(*points))]
    actual_angles.append(np.rad2deg(np.arctan(abs(deltas[1])/-deltas[0])))
    points = []
print(actual_angles)
print(calib_angles)
# When everything done, release the video capture object and close all frames
cap.release()
cv2.destroyAllWindows()
#save to file
pickle.dump({**calib,"angle_act":actual_angles,"angle_calib":calib_angles},open(args["output_file"],'wb'))
