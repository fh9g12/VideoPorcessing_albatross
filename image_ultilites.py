"""
Doc string
"""
import sys
import os
import argparse

import cv2
import numpy as np

def crop_image(img,bb):
    if bb is None:
        return img
    else:
        return img[bb[1]:bb[1]+bb[3],bb[0]:bb[0]+bb[2]]

def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

def selectROIResized(prompt,img, height, flip = False, inter=cv2.INTER_AREA):
    if flip:
        img = cv2.flip(img,-1)
    (h, w) = img.shape[:2]
    img = ResizeWithAspectRatio(img,height = height,inter = inter)
    ratio = h/height
    roi = cv2.selectROI(prompt, img, False)
    roi = tuple(int(val*ratio) for val in roi)
    if flip:
        roi = (w-roi[0]-roi[2],h-roi[1]-roi[3],roi[2],roi[3])
    return roi

def undistort_image(frame,focal_length,coeffs):
    # Setup Matricies
    distCoeff = np.zeros((4,1),np.float64)
    cam = np.eye(3,dtype=np.float32)
    # extract coeffs
    k1,k2,p1,p2 = coeffs

    width  = frame.shape[1]
    height = frame.shape[0]

    distCoeff[0,0] = k1
    distCoeff[1,0] = k2
    distCoeff[2,0] = p1
    distCoeff[3,0] = p2

    cam[0,2] = width/2.0  # define center x
    cam[1,2] = height/2.0 # define center y
    cam[0,0] = focal_length        # define focal length x
    cam[1,1] = focal_length       # define focal length y
    return cv2.undistort(frame,cam,distCoeff)

def getMeanFrame(video_capture,roi=None,startTime = 0,interval = None):
    #get video Properties
    total_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    duration = total_frames/fps

    #pick start frame
    last_frame = int(total_frames)
    if startTime<0:
        first_frame = int((duration-5)*fps)
    else:
        first_frame = int(startTime*fps)
        if startTime + interval < duration:
            last_frame = int((startTime + interval)*fps)
    
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, first_frame-1)
    bg_frames = last_frame - first_frame
    ret,_bg = video_capture.read()
    if roi is not None:
        _bg = crop_image(_bg,roi)
    _bg = _bg.astype('float')
    for i in range(first_frame,last_frame-1):
        ret,tmp_bg = video_capture.read()
        if ret:
            if roi is not None:
                tmp_bg = crop_image(tmp_bg,roi)
            _bg += tmp_bg.astype('float')
    _bg /= bg_frames
    _bg = _bg.astype('uint8')
    return _bg
