#!/usr/bin/python

import pickle
import re
import time
import os
from itertools import groupby
from ConfigParser import *
from Tkinter import *

class drawThings(object):
    def __init__(self):
        self.root = Tk()
        self.servoMap = {'0': 1, '1': 0, '2': 2, '3': 3} 

        self.canvasWidth = 400
        self.centerWidth = self.canvasWidth / 2
        centerW = self.centerWidth

        self.canvasHeight = 400
        self.centerHeight = self.canvasHeight / 2
        centerH = self.centerHeight

        self.canvas = Canvas(self.root, width=self.canvasWidth, height = self.canvasHeight)
        self.irisW = 40
        self.irisH = 40
        self.irisPosition = (self.angleRange(90,1),
                             self.angleRange(90,1))

        self.iris = self.canvas.create_oval(centerW - self.irisW / 2,
                                            centerH - self.irisH / 2,
                                            centerW + self.irisW / 2,
                                            centerH + self.irisH / 2,
                                            outline='white', fill='blue')

        self.lidTopPosition = (self.angleRange(90,1),
                               self.angleRange(90,1))

        self.lidTopWidth = 200
        self.lidTop = self.canvas.create_line(centerW - self.lidTopWidth/2,
                                              centerH,
                                              centerW + self.lidTopWidth/2,
                                              centerH)
        self.lidBottomPosition = (self.angleRange(90,1),
                               self.angleRange(90,1))

        self.lidBottomWidth = 200
        self.lidBottom = self.canvas.create_line(centerW - self.lidBottomWidth/2,
                                                 centerH,
                                                 centerW + self.lidBottomWidth/2,
                                                 centerH,
                                                 fill='blue')

        self.canvas.pack()

    def centerParts(self):
        self.updateLidTop(90)
        self.updateLidBottom(90)
        self.updateIrisHor(90)
        self.updateIrisVir(90)
        self.canvas.update()

    def displayAnimation(self, data):
        if len(data) == 0: 
            print ("nothing to play")
            return()

        counter = 0.0
        for i in range(0,len(data)):
            servo, angle = data[i]['pos_str'].split()
            servo = self.servoMap[servo]
            angle = int(angle)
            counter = float(counter + data[i]['delta'])
            # print "%lf :: %d :: %d" % (counter, servo, angle)
            if (servo == 0):
                self.updateLidTop(angle)
            if (servo == 1):
                self.updateLidBottom(angle)
            if (servo == 2):
                self.updateIrisHor(angle)
            if (servo == 3):
                self.updateIrisVir(angle)

            time.sleep(.0100)
            self.canvas.update()



    def updateLidTop(self, angle):
        (x, y) = self.lidTopPosition
        new = self.angleRange(angle,1)
        self.lidTopPosition = (x, new)
        self.canvas.move(self.lidTop, 0, new - y)

    def updateLidBottom(self, angle):
        (x, y) = self.lidBottomPosition
        new = self.angleRange(angle,1)
        self.lidBottomPosition = (x, new)
        self.canvas.move(self.lidBottom, 0, new - y)

    def updateIrisHor(self, angle):
        (x, y) = self.irisPosition
        new = self.angleRange(angle,1)
        self.irisPosition = (new, y)
        self.canvas.move(self.iris, new - x, 0)

    def updateIrisVir(self, angle):
        (x, y) = self.irisPosition
        new = self.angleRange(angle,1)
        self.irisPosition = (x, new)
        self.canvas.move(self.iris, 0, new - y)

    def angleRange(self, angle, factor):
        return(int(angle - 90 * factor))

    def servoSlowMove(self, a2, b2, c2, d2, inc):
        (a1, b1, c1, d1) = self.ServoCurrentPos()
        i1 = float(a2 - a1) / inc
        i2 = float(b2 - b1) / inc
        i3 = float(c2 - c1) / inc
        i4 = float(d2 - d1) / inc
        for i in range(0, inc):
            a1 = float(a1) + i1
            b1 = float(b1) + i2
            c1 = float(c1) + i3
            d1 = float(d1) + i4
            self.ServoMove(0, int(a1))            
            self.ServoMove(1, int(b1))            
            self.ServoMove(2, int(c1))            
            self.ServoMove(3, int(d1))            

    def servoCenter(self):
        self.ServoSlowMove(90,90,90,90,40)


class recorderHandler:
    def __init__(self):
        FileName = re.sub(r'\.py$', "", os.path.abspath( __file__ )) + '.ini'

        self.joyreverse = [0,1,0,0,0]
        self.cp=ConfigParser()
        try:
            self.cp.readfp(open(FileName,'r'))
        except IOError:
            raise Exception,'NoFileError'

        self.recordingFile = self.cp.get('Variables', 'recording_file')
        try:
            with open(self.recordingFile) as f: pass
            self.rdata = pickle.load(open(self.recordingFile, "rb"))
        except IOError as e:
            print "no data"

    def getData(self,name):
        l = pickle.load(open(self.recordingFile, "rb"))
        r = 0
        for i in l:
            if l[i]['name'] == name:
                r = l[i]['data']
                break
        return(self.processBits(r))

    def getNames(self):
        l = pickle.load(open(self.recordingFile, "rb"))
        j = []
        for i in l:
            j.extend([l[i]['name']])
        return(j)

    def listNames(self):
        l = self.getNames()
        for n in l:
            print n

    def playBack(self, name):
        bits = self.getData(name)
        self.bits = bits

        if len(bits) == 0: 
            print "nothing to play: " + name
        else:
            # self.ServoCenter()
            counter = 0
            for i in range(0,len(bits)):
                servo, angle = bits[i]['pos_str'].split()
                counter = counter + bits[i]['delta']
                # print "%lf :: %d :: %d" % (float(counter), int(servo), int(angle))
                # time.sleep(bits[i]['delta'])
                # self.ServoMove(int(servo), int(angle))

    def processBits(self,rows):
        # this removes duplicates, easy. 
        rows = [ key for key,_ in groupby(rows)]
        l = {}
        for i in range(0,len(rows)):
            l[i] = {}
            t, l[i]['pos_str'] = rows[i].split(' ', 1)
            seconds, useconds = t.split(':')
            l[i]['time'] = float("%2.6lf" % float(seconds + "." + useconds))

        pos_old = l[0]['pos_str']
        # t_old = l[0]['time']
        t_old = 0
        new = {}
        count = 0
        for i in range(1,len(rows)):
            pos = l[i]['pos_str']
            t = l[i]['time']
            if pos != pos_old:
                new[count] = {}
                new[count]['delta'] = l[i]['time'] - t_old
                new[count]['pos_str'] = pos_old
                pos_old = pos
                t_old = t
                count = count + 1
        new[count] = {}
        new[count]['delta'] = l[i]['time'] - t_old
        new[count]['pos_str'] = pos_old
        return new

if __name__ == "__main__":
    dt = drawThings()
    s = recorderHandler()

    for name in s.getNames():
        print name
        bits = s.getData(name)
        dt.centerParts()
        time.sleep(.400)
        dt.displayAnimation(bits)
        time.sleep(.8)
