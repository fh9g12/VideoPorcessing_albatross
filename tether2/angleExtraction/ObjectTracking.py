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

def drawBox(img,bb):
    x,y,w,h = (int(b) for b in bb)
    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,100),3,1)
    return img
def getBoxCentreInfo(box,index = 1):
    x,y,w,h = box
    return {f'x{index}':x+w/2,f'y{index}':y+h/2}

def get_frame(vid_cap,ROI,mtx,dist):
    ret,frame = vid_cap.read()
    roi = crop_image(frame,ROI)
    roi = cv2.undistort(roi, mtx, dist, None, mtx)
    roi = cv2.GaussianBlur(roi,(3,3),0)
    return roi

def select_points(img):
    p = []
    time = [0]
    def mouse_click(event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            time[0] = timer()
        elif event == cv2.EVENT_LBUTTONUP:
            if (timer() - time[0])<0.2:
                p.append((x,y))

    # select ROIs
    cv2.namedWindow("img")
    cv2.setMouseCallback("img", mouse_click)
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):
            break
        if key == ord("d"):
            if len(p)>0:
                p.pop()
        tmp_frame = img.copy()    
        for p_i in p:
            tmp_frame[p_i[1],p_i[0]] = [0,0,255]     
        cv2.imshow('img',tmp_frame)
    return p

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
ap.add_argument("-s", "--start_frame",type=int, default = 0, help = "Frame to start at")
ap.add_argument("-o", "--output_file", help = "Output file name")
ap.add_argument("-t", "--tracker", type=str, default="kcf",
	help="OpenCV object tracker type")
ap.add_argument("-d","--display_video", type=str2bool, default=False, help="Show video")
ap.add_argument("-c","--calib_file", required=True, help="camera calibration file")
ap.add_argument("-w", "--roi_width", type=int, help = "width of square around ROIs")
args = vars(ap.parse_args())

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    #"boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    #"tld": cv2.TrackerTLD_create,
    #"medianflow": cv2.TrackerMedianFlow_create,
    #"mosse": cv2.TrackerMOSSE_create,
}

# load the calibration file
calib = pickle.load(open(args["calib_file"],'rb'))
frameROI = calib["roi"]
# generate camera calibration matrix
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera([calib["threedpoints"]], [calib["twodpoints"]], tuple(calib['roi'][i] for i in [2,3]), None, None)

# grab the appropriate object tracker using our dictionary of
# OpenCV object tracker objects
print('Loading Video')

# get reqired frame
cap = cv2.VideoCapture(args['video'])
print(cap.get(cv2.CAP_PROP_FPS))
cap.set(cv2.CAP_PROP_POS_FRAMES, args['start_frame'])
roi = get_frame(cap,frameROI,mtx,dist)

# figure out if its the left or right FWT
side = "Left" if frameROI[0]<1000 else "Right"

frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
fps = cap.get(cv2.CAP_PROP_FPS)
period = 1/fps

res = []
cap.set(cv2.CAP_PROP_POS_FRAMES, args['start_frame'])
tracking_setup = False
pause = True
tracking = False
trackers = []
i = args['start_frame']
pbar = tqdm(total=int(frame_count - args['start_frame']-1))
cv2.namedWindow("img",cv2.WINDOW_KEEPRATIO)
while i < int(frame_count)-1:
    skip = False
    key = cv2.waitKey(10) & 0xFF
    if key == ord("f"):
        break
    if key == ord("t"):
        tracking_setup = False
        tracking = False
    if key == ord(" "):
        pause = not pause

    if not tracking_setup:
        trackers = []
        points = select_points(roi)

        #create ROIs
        w = args["roi_width"]
        ROIs = [[xc-w/2,yc-w/2,w,w] for xc,yc in points]

        # ROIs = cv2.selectROIs('Select Objects to track', roi, False)
        #print(ROIs)
        for ROI in ROIs:
            tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
            tracker.init(roi,ROI)
            trackers.append(tracker)
        tracking_setup = True
        pause = False
        tracking = True

    if (tracking and not pause) or (pause and key == ord("s")):
        (tracking_successful,boxes) = zip(*(t.update(roi) for t in trackers ))
        res_dict = {"Frame":i,"fps":fps,"Side":side}
        tracking = all(tracking_successful)
        if tracking:
            for j,box in enumerate(boxes):
                roi = drawBox(roi,box)     
                res_dict = {**res_dict,**getBoxCentreInfo(box,j)}
            cv2.putText(roi,f"Tracking, frame: {i}",(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0,2))      
        else:
            cv2.putText(roi,f"Lost, frame: {i}",(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255,2))
            pause = True
        res.append(res_dict)
    # if pause:   
    cv2.imshow("img",roi)

    if (tracking and not pause) or (pause and key == ord("s")):
        roi = get_frame(cap,frameROI,mtx,dist)
        i+=1
        pbar.update(1)
pbar.close()
# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()

df = pd.DataFrame(res)
df.to_csv(args["output_file"])

