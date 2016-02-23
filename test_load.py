#!/usr/bin/env python

import pickle
import re
import time
import os
from itertools import groupby
from ConfigParser import *

class servoHandler:
    def __init__(self):
        FileName = re.sub(r'\.py$', "", os.path.abspath( __file__ )) + '.ini'
        self.joymap = [3,4,1,2] # link between joystick and the servo to move
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
                print "%lf :: %d :: %d" % (float(counter), int(servo), int(angle))
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

    def servoMove(self,servo, angle):
        self.ServoLoadString(servo, angle)
        servo = self.joymap[servo]
        if self.joyreverse[servo]:
            angle = 180 - angle
        if (0 <= angle <= 180):
            self.ser.write(chr(255))
            self.ser.write(chr(servo))
            self.ser.write(chr(angle))
        else:
            print "Servo angle must be an integer between 0 and 180.\n"

if __name__ == "__main__":
    d = servoHandler()
    d.playBack("frickinpeople")
