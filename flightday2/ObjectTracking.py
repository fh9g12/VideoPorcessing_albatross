import numpy as np 
import cv2
import os
import sys
import argparse
import pandas as pd

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

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required = True, help = "Video To pass")
ap.add_argument("-o", "--output_file", help = "Output file name")
ap.add_argument("-t", "--tracker", type=str, default="kcf",
	help="OpenCV object tracker type")
ap.add_argument("-d","--display_video", type=str2bool, default=False, help="Show video")
ap.add_argument("-s", "--start_frame",type=int, default = 0, help = "Frame to start at")
args = vars(ap.parse_args())

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create,
    "goturn": cv2.TrackerGOTURN_create
}
# grab the appropriate object tracker using our dictionary of
# OpenCV object tracker objects
trackers = cv2.MultiTracker_create()

print('Loading Video')


# Select ROI to perform analysis in
cap = cv2.VideoCapture(args['video'])
print(cap.get(cv2.CAP_PROP_FPS))
cap.set(cv2.CAP_PROP_POS_FRAMES, args['start_frame'])
ret,frame = cap.read()
frameROI = selectROIResized('Select ROI',frame,700)
# ROIs = cv2.selectROIs('Select ROIs', frame, False)
# frameROI = ROIs[0].copy()

# figure out if its the left or right FWT
(h, w) = frame.shape[:2]
side = "Left" if frameROI[0]+(frameROI[2]/2)<w/2 else "Right"




# Select Tracking object
roi = crop_image(frame,frameROI)
roi = cv2.resize(roi, (0,0), fx=2, fy=2) 
roi = cv2.GaussianBlur(roi,(3,3),0)
#roi = cv2.Canny(roi,100,255)

ROIs = cv2.selectROIs('Select Objects to track', roi, False)
print(ROIs)
for ROI in ROIs:
    tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
    trackers.add(tracker, roi, tuple(ROI))

def drawBox(img,bb):
    x,y,w,h = (int(b) for b in bb)
    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,100),3,1)
    return img
def getBoxCentreInfo(box,index = 1):
    x,y,w,h = box
    return {f'x{index}':x+w/2,f'y{index}':y+h/2}


frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
fps = cap.get(cv2.CAP_PROP_FPS)
period = 1/fps

res = []
cap.set(cv2.CAP_PROP_POS_FRAMES, args['start_frame'])
for i in range(args['start_frame'],int(frame_count)):
    key = cv2.waitKey(10) & 0xFF
    if key == ord("c"):
        break
    ret,frame = cap.read()
    roi = crop_image(frame,frameROI)
    roi = cv2.resize(roi, (0,0), fx=2, fy=2) 
    roi = cv2.GaussianBlur(roi,(3,3),0)
    #roi = cv2.Canny(roi,100,255)
    (success, boxes) = trackers.update(roi)
    res_dict = {"Frame":i,"fps":fps,"Side":side}
    if success:
        for j,box in enumerate(boxes):
            roi = drawBox(roi,box)     
            res_dict = {**res_dict,**getBoxCentreInfo(box,j)}
        cv2.putText(roi,"Tracking",(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0,2))      
    else:
        cv2.putText(roi,"Lost",(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255,2)) 
    cv2.imshow('frame',roi)
    res.append(res_dict)

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()


df = pd.DataFrame(res)
df.to_csv(args["output_file"])








