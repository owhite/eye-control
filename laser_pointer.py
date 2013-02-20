#!/usr/bin/python

import sys
import cv

# definition of some constants
cam_width = 640
cam_height = 480

# HSV color space Threshold values for a RED laser pointer 
# hue
hmin = 5 
hmax = 6 # hmax = 180
# saturation
smin = 50
smax = 100
# value
vmin = 250
vmax = 256

#############################################################################

def create_and_position_window(name, xpos, ypos):
    ''' a function to created a named widow (from name), 
        and place it on the screen at (xpos, ypos) '''
    cv.NamedWindow(name, 1 ) 
    cv.ResizeWindow(name, cam_width, cam_height) # resize it
    cv.MoveWindow(name, xpos, ypos) # move it to (xpos,ypos) on the screen

def setup_camera_capture(device_num=0):
    ''' perform camera setup for the device number (default device = 0) i
        return a reference to the camera Capture
    '''
    try:
        # try to get the device number from the command line
        device = int(device_num)
    except (IndexError, ValueError):
        # no device number on the command line, assume we want the 1st device
        device = 0
    print 'Using Camera device %d'%device

    # no argument on the command line, try to use the camera
    capture = cv.CreateCameraCapture (device)

    if not capture:
        print "Error opening capture device"
        sys.exit (1)
    
    return capture    

# so, here is the main part of the program
def main():

    # create windows 
    create_and_position_window('Thresholded_HSV_Image', 10, 10)
    create_and_position_window('RGB_VideoFrame', 10+cam_width, 10)

    create_and_position_window('Hue', 10, 10+cam_height)
    create_and_position_window('Saturation', 210, 10+cam_height)
    create_and_position_window('Value', 410, 10+cam_height)
    create_and_position_window('LaserPointer', 0,0)

    capture = setup_camera_capture()

    # create images for the different channels
    h_img = cv.CreateImage ((cam_width,cam_height), 8, 1)
    s_img = cv.CreateImage ((cam_width,cam_height), 8, 1)
    v_img = cv.CreateImage ((cam_width,cam_height), 8, 1)
    laser_img = cv.CreateImage ((cam_width,cam_height), 8, 1)
    cv.SetZero(h_img)
    cv.SetZero(s_img)
    cv.SetZero(v_img)
    cv.SetZero(laser_img)

    while True: 
        # 1. capture the current image
        frame = cv.QueryFrame (capture)
        if frame is None:
            # no image captured... end the processing
            break

        hsv_image = cv.CloneImage(frame) # temporary copy of the frame
        cv.CvtColor(frame, hsv_image, cv.CV_BGR2HSV) # convert to HSV

        # split the video frame into color channels
        cv.Split(hsv_image, h_img, s_img, v_img, None)

        # Threshold ranges of HSV components.
        cv.InRangeS(h_img, hmin, hmax, h_img)
        cv.InRangeS(s_img, smin, smax, s_img)
        cv.InRangeS(v_img, vmin, vmax, v_img)

        # Perform an AND on HSV components to identify the laser!
        cv.And(h_img, v_img, laser_img)
        # This actually Worked OK for me without using Saturation.
        #cv.cvAnd(laser_img, s_img,laser_img) 

        # Merge the HSV components back together.
        cv.Merge(h_img, s_img, v_img, None, hsv_image)

        #-----------------------------------------------------
        # NOTE: default color space in OpenCV is BGR!!
        # we can now display the images 
        cv.ShowImage ('Thresholded_HSV_Image', hsv_image)
        cv.ShowImage ('RGB_VideoFrame', frame)
        cv.ShowImage ('Hue', h_img)
        cv.ShowImage ('Saturation', s_img)
        cv.ShowImage ('Value', v_img)
        cv.ShowImage('LaserPointer', laser_img)

        # handle events
        k = cv.WaitKey (10)

        if k == '\x1b' or k == 'q':
            # user has press the ESC key, so exit
            break


if __name__ == '__main__':
    main()
