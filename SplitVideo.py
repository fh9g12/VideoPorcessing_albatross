import numpy as np 
import cv2
import os
import sys
import argparse
import matplotlib.pyplot as plt
import torch

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required = True, help = "Video To pass")
ap.add_argument("-f", "--folder", required = True, help = "folder to dump images")
args = vars(ap.parse_args())



cap = cv2.VideoCapture(args['video'])

success,image = cap.read()
count = 0
while success:
  cv2.imwrite(f"{args['folder']}frame{count}.jpg", image)     # save frame as JPEG file      
  success,image = cap.read()
  print('Read a new frame: ', success)
  count += 1
