#!/usr/bin/env python

STORE=True # write output video?
OUTPUT="thing.avi"
CAMERAID=-2 # -1 for auto, -2 for video
HAARCASCADE="/usr/local/share/OpenCV/haarcascades/haarcascade_eye.xml"

# Internal parameters
FPS = 25 # target FPS
XWINDOWS = 3 # how many windows on x axis
WORKING_HEIGHT = 300 # size of image to work with, 300 is okay
CLOCKS_PER_SEC = 1.0
MHI_DURATION = .1
MAX_TIME_DELTA = 0.5
MIN_TIME_DELTA = 0.05

import cv
import time
import sys
import math

class Source:
    def __init__(self, id, flip=True):
        self.capture = cv.CaptureFromCAM(0)

    def grab_frame(self):
        self.frame = cv.QueryFrame(self.capture)
        if not self.frame:
            print "can't grap frame, or end of movie. Bye bye."
            sys.exit(2)
        cv.Flip(self.frame, None, 1)
        return self.frame

class Setup:
    def __init__(self):
        self.source = Source(CAMERAID)
        self.height_value = 30
        self.jitter_value = 18
        self.count = -1
        self.storage = cv.CreateMemStorage(0)
        self.last = 0
        self.old_center = (0,0)

        self.orig = self.source.grab_frame()

        self.width = self.orig.width
        self.height = self.orig.height
        self.size = (self.width, self.height)
        self.smallheight = WORKING_HEIGHT
        self.smallwidth = int(self.width * self.smallheight/self.height * 1.0)
        self.smallsize = (self.smallwidth, self.smallheight)

        # alloc mem for images
        self.small = cv.CreateImage(self.smallsize, cv.IPL_DEPTH_8U, 3)
        self.motion = cv.CreateImage(self.smallsize, cv.IPL_DEPTH_8U, 3)
        self.eye = cv.CreateImage(self.smallsize, cv.IPL_DEPTH_8U, 3)
        self.mhi = cv.CreateImage(self.smallsize, cv.IPL_DEPTH_32F, 1)
        self.orient = cv.CreateImage(self.smallsize,cv.IPL_DEPTH_32F, 1)
        self.segmask = cv.CreateImage(self.smallsize,cv.IPL_DEPTH_32F, 1)
        self.mask = cv.CreateImage(self.smallsize,cv.IPL_DEPTH_8U, 1)
        self.temp = cv.CreateImage(self.smallsize, cv.IPL_DEPTH_8U, 3)
        self.buf = range(10) 
        self.n_frames = 4
        for i in range(self.n_frames):
            self.buf[i] = cv.CreateImage(self.smallsize, cv.IPL_DEPTH_8U, 1)
            cv.SetZero(self.buf[i])

        self.combined = cv.CreateImage((self.smallwidth * XWINDOWS, self.smallheight), cv.IPL_DEPTH_8U, 3)

        # make matrix for erode/dilate
        MORPH_SIZE = 3
        center = (MORPH_SIZE / 2) + 1
        self.morpher_small = cv.CreateStructuringElementEx(MORPH_SIZE, MORPH_SIZE, center, center, cv.CV_SHAPE_ELLIPSE)
        MORPH_SIZE = 11
        center = (MORPH_SIZE / 2) + 1
        self.morpher = cv.CreateStructuringElementEx(MORPH_SIZE, MORPH_SIZE, center, center, cv.CV_SHAPE_ELLIPSE)

        if STORE:
            self.writer = cv.CreateVideoWriter(OUTPUT, 0, 15, cv.GetSize(self.combined), 1)

        # make window
        cv.NamedWindow("Skin Detection") 

        cv.CreateTrackbar('Height', 'Skin Detection', self.height_value,
                          100, self.change_height)

        cv.CreateTrackbar('Jitter', 'Skin Detection', self.jitter_value,
                          100, self.change_jitter)

        # cv.NamedWindow( "Histogram", 1 )

    def process_motion(self,img):
        center = (-1, -1)
        timestamp = time.clock() / CLOCKS_PER_SEC # get current time in seconds
        idx1 = self.last
        cv.CvtColor(img, self.buf[self.last], cv.CV_BGR2GRAY) # convert frame to grayscale
        idx2 = (self.last + 1) % self.n_frames 
        self.last = idx2
        silh = self.buf[idx2]
        cv.AbsDiff(self.buf[idx1], self.buf[idx2], silh) # get difference between frames
        cv.Threshold(silh, silh, 30, 1, cv.CV_THRESH_BINARY) # and threshold it
        cv.UpdateMotionHistory(silh, self.mhi, timestamp, MHI_DURATION) # update MHI
        cv.ConvertScale(self.mhi, self.mask, 255./MHI_DURATION,
                    (MHI_DURATION - timestamp)*255./MHI_DURATION)
        cv.SetZero(img)
        cv.Merge(self.mask, None, None, None, img)
        cv.CalcMotionGradient(self.mhi, self.mask, self.orient, MAX_TIME_DELTA, MIN_TIME_DELTA, 3)
        seq = cv.SegmentMotion(self.mhi, self.segmask, self.storage, timestamp, MAX_TIME_DELTA)
        inc = 0
        a_max = 0
        max_rect = -1
    
        # find the biggest change on the image
        for (area, value, comp_rect) in seq:
            if comp_rect[2] + comp_rect[3] > 100: # reject very small components
                if area > a_max: 
                    a_max = area
                    max_rect = inc
            inc += 1
    
        if max_rect != -1:
            (area, value, comp_rect) = seq[max_rect]
            color = cv.CV_RGB(255, 0,0)
            silh_roi = cv.GetSubRect(silh, comp_rect)
                # calculate number of points within silhouette ROI
            count = cv.Norm(silh_roi, None, cv.CV_L1, None)
            magnitude = 30.
            y1 = int(comp_rect[1] + (comp_rect[3] * (float(self.height_value) / 100)))

            # print '%d %lf %lf' % (y1, y2, float(self.height_value / 100))
            center = ((comp_rect[0] + comp_rect[2] / 2), y1)

            cv.Rectangle(self.motion, (comp_rect[0], comp_rect[1]), 
                         (comp_rect[0] + comp_rect[2], comp_rect[1] + comp_rect[3]), (0,0,255), 1)

        return center


    def pipeline(self):
        presentation = []
        self.orig = self.source.grab_frame()
        cv.Resize(self.orig, self.small)

        size = self.smallsize

        presentation.append((self.small, 'raw'))

        self.motion = cv.CloneImage(self.small)

        center = self.process_motion(self.motion)

        if center != (-1,-1):
            cv.Circle(self.motion, center, cv.Round(30), cv.CV_RGB(0,225,0), 3, cv.CV_AA, 0)

        presentation.append((self.motion, 'motion')) 

        self.eye = cv.CloneImage(self.small)

        if center == (-1,-1):
            cv.Circle(self.eye, self.old_center, cv.Round(30 * .7), cv.CV_RGB(0,225,0), 3, cv.CV_AA, 0)
            self.old_center = self.old_center

            x = '%d %0.3lf :: %d %d :: %d %d' % (0, 0, 0, 0, self.old_center[0], self.old_center[1])


        else:
            x1 = self.old_center[0]
            y1 = self.old_center[1]
            x2 = center[0]
            y2 = center[1]
            dx = x2 - x1
            dy = y2 - y1
            d = math.sqrt( (dx)**2 + (dy)**2 )
            angle = math.atan2(dy, dx)

            if d > self.jitter_value: 
                self.old_center = (x2, y2)

                (x3, y3) = (cv.Round(x1 + self.jitter_value * math.cos(angle)),
                            cv.Round(y1 + self.jitter_value * math.sin(angle)))

                self.old_center = (cv.Round(x1 + self.jitter_value * math.cos(angle)),
                                   cv.Round(y1 + self.jitter_value * math.sin(angle)))

                cv.Circle(self.eye, self.old_center, 30, cv.CV_RGB(255,0,0), 3, cv.CV_AA, 0)
            else:
                self.old_center = (x2, y2)
                cv.Circle(self.eye, self.old_center, 30, cv.CV_RGB(0,225,0), 3, cv.CV_AA, 0)

        presentation.append((self.eye, 'final'))

         # combine and show the results
        combined = self.combine_images(presentation)
        cv.ShowImage('Difference thing', combined )

        if STORE:
            cv.WriteFrame(self.writer, self.combined)

    def change_jitter(self, position):
        self.jitter_value = position

    def change_height(self, position):
        self.height_value = position

    def combine_images(self, images):

        font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1.4, 1.4, 0, 2, 8)

        for i,(image, name) in enumerate(images):
            if image.nChannels == 1:
                cv.Merge(image, image, image, None, self.temp)
            else:
                cv.Copy(image, self.temp)
            xoffset = (i % XWINDOWS) * self.smallsize[0]
            yoffset = (i / XWINDOWS) * self.smallsize[1]
            cv.SetImageROI(self.combined, (xoffset, yoffset, self.smallsize[0],
                self.smallsize[1]))
            cv.Copy(self.temp, self.combined)
            cv.PutText(self.combined, name, (5, 40), font, (30, 200, 200))
            cv.ResetImageROI(self.combined)
        return self.combined

    def run(self):
        self.first_frame = True
        while True:
            t = time.time()

            self.pipeline()

            wait = max(2, (1000/FPS)-int((time.time()-t)*1000))
            cv.WaitKey(wait)

if __name__ == '__main__':
    s=Setup()
    s.run()




