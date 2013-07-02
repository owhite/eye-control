#!/usr/bin/env python

import pygame
import random
from itertools import groupby
import time
import serial
import recorder_handlers
from ConfigParser import *

class application:
    def __init__(self, file):
        # Initialize the things
        self.time_since_event = time.time()
        self.ini_file = file
        self.LoadIniData()
        self.joymap = [3,4,1,2] # link between joystick and the servo to move
        self.joyreverse = [0,1,0,0,0]
        self.servo_pos = []
        for i in self.joymap:
            self.servo_pos.append(90)

        usbport = self.cp.get('Variables', 'usbport')
        try:
            self.ser = serial.Serial(usbport, 9600, timeout=1)
        except:
            print "   did you plug something into " + usbport + "? an eyeball for example?"
            exit()

        f = self.cp.get('Variables', 'recording_file')
        self.rdata = recorder_handlers.RecordingData(f)
        self.playlist = self.rdata.get_names()

        pygame.init()
        self.pygame = pygame
        if(pygame.joystick.get_count() < 1):
            # no joysticks found
            print "Please connect a joystick.\n"
            self.Quit()
        else:
            # create joystick object from first joystick in list
            self.Joy0 = pygame.joystick.Joystick(0)
            self.Joy0.init()

    def find_events(self):
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN:
                if (e.dict['button'] == 5):
                    print "button 5"
                if (e.dict['button'] == 7):
                    print "button 7"
                    quit()

            if e.type == pygame.JOYAXISMOTION:
                pos = e.dict['value']
                pos = int(90 + round(pos * 90, 0))
                n = e.dict['axis']
                if (n >= 0 and n < 5):
                    # constructs the string that reflects joystick
                    #  position
                    self.ServoMove(n,pos)
                    self.time_since_event = time.time()

    def PlayBack(self, name):
        bits = self.rdata.get_data(name)
        cointossresult = random.randrange(0,100)
        # cointossfreq is a percentage of the time we'll do nothing
        cointossfreq = 30
        if cointossresult < cointossfreq:
            print "pausing"
        else :
            print "next thing: %s" % name

        if len(bits) == 0:
            print "This name: %s is not in the recording file" % name
        else:
            bits = self.ProcessBits(bits)
            self.ServoCenter()
            counter = 0
            for i in range(0,len(bits)):
                self.find_events()
                while(time.time() - self.time_since_event < 1):
                    self.find_events()
                servo, angle = bits[i]['pos_str'].split()
                time.sleep(bits[i]['delta'])
                if cointossresult >= cointossfreq:
                    self.ServoMove(int(servo), int(angle))

    def LoadIniData(self):
        FileName = self.ini_file
        self.cp=ConfigParser()
        try:
            self.cp.readfp(open(FileName,'r'))
	# f.close()
        except IOError:
            raise Exception,'NoFileError'
        return

    def ProcessBits(self,rows):
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

    def ServoSlowMove(self, a2, b2, c2, d2, inc):
        (a1, b1, c1, d1) = self.servo_pos
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

    def ServoCenter(self):
        self.ServoSlowMove(90,90,90,90,40)

    def ServoMove(self,servo, angle):
        self.servo_pos[servo] = angle
        servo = self.joymap[servo]
        if self.joyreverse[servo]:
            angle = 180 - angle
        if (0 <= angle <= 180):
            self.ser.write(chr(255))
            self.ser.write(chr(servo))
            self.ser.write(chr(angle))
        else:
            print "Servo angle must be an integer between 0 and 180.\n"

    def ServoMove(self,servo, angle):
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
    a = application('./recorder.ini')
    while (1):
        play_this = a.playlist[random.randrange(len(a.playlist))]
        a.PlayBack(play_this)
    quit()
