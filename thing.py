#!/usr/bin/env python

import cv
import time

cv.NamedWindow("camera", 1)
capture = cv.CreateCameraCapture(0)

width = 320
height = 240

if width is None:
    width = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH))
else:
	cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH,width)    

if height is None:
	height = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT))
else:
	cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT,height) 

while True:
    img = cv.QueryFrame(capture)
    cv.ShowImage("camera", img)
    k = cv.WaitKey(10);
    if k == 'f':
        break
