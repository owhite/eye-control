#!/usr/bin/python

# Find value of a pixel on a screen 

import cv

global h,s,v,i,im,evente  
hsv_string = ""
pos_string = ""

def my_mouse_callback(event,x,y,flags,param):
	global evente,h,s,v,i,r,g,b,j
	global hsv_string
	global pos_string
	evente=event
	# Here event is left mouse button double-clicked
	if event==cv.CV_EVENT_LBUTTONDBLCLK:
		hsv=cv.CreateImage(cv.GetSize(frame),8,3)
		cv.CvtColor(frame,hsv,cv.CV_BGR2HSV)
		(h,s,v,i)=cv.Get2D(hsv,y,x)
		(r,g,b,j)=cv.Get2D(frame,y,x)

		hsv_string = str(cv.Get2D(hsv,y,x))
		pos_string = '%s, %s' % (x, y)

#	Thresholding function	(from earlier mouse_callback.py)	
def getthresholdedimg(im):
	imghsv=cv.CreateImage(cv.GetSize(im),8,3)
	cv.CvtColor(im,imghsv,cv.CV_BGR2HSV)
	imgthreshold=cv.CreateImage(cv.GetSize(im),8,1)
	cv.InRangeS(imghsv,cv.Scalar(h,100,10),cv.Scalar(h+10,255,255),imgthreshold)
	return imgthreshold
	
def getpositions(im):
	leftmost=0
	rightmost=0
	topmost=0
	bottommost=0
	temp=0
	for i in range(im.width):
		col=cv.GetCol(im,i)
		if cv.Sum(col)[0]!=0.0:
			rightmost=i
			if temp==0:
				leftmost=i
				temp=1		
	for i in range(im.height):
		row=cv.GetRow(im,i)
		if cv.Sum(row)[0]!=0.0:
			bottommost=i
			if temp==1:
				topmost=i
				temp=2	
	return (leftmost,rightmost,topmost,bottommost)
	
capture=cv.CaptureFromCAM(1)
frame=cv.QueryFrame(capture)
test=cv.CreateImage(cv.GetSize(frame),8,3)

# 	Now the selection of the desired color from video.( new)
cv.NamedWindow("pick")
string = cv.SetMouseCallback("pick",my_mouse_callback)

font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1.4, 1.4, 0, 2, 8)

print "Select a spot on screen, double click to get hsv value"
while(1):
	frame=cv.QueryFrame(capture)
	cv.PutText(frame, pos_string, (5, 40), font, (30, 200, 200))
	cv.PutText(frame, hsv_string, (5, 80), font, (30, 200, 200))

	cv.ShowImage("pick",frame)
	if cv.WaitKey(10) == 27: 
            break

cv.DestroyWindow("pick")


