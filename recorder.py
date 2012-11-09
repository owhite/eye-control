#!/usr/bin/env python

import os
import re
import sys
import time
import serial
from itertools import groupby
import Tkinter
import tkMessageBox
import recorder_handlers
from ConfigParser import *

# Handles the layout of the root window
class tk_layout:
    def __init__(self, parent, stopwatch, ser):
        parent.title("recorder")
        self.parent = parent
        tk = Tkinter
        self.stopwatch = stopwatch
        self.ser = ser

	self.sp1 = tk.Label(self.parent)
	self.sp1.grid(row=0)

        # Current time
        self.startstop_string = tk.StringVar(value="Start")
        self.time_string = tk.StringVar(value="00.000000")
        self.microseconds = 0
        self.lTime = tk.Label(self.parent, textvariable=self.time_string, 
                              font=('Fixed', 14))
        self.lTime.grid(row=1, column=0, sticky=tk.W, columnspan=4)

        # Information about joystick positions
        self.servo_string = tk.StringVar(value="090 090 090 090")
	self.lServo = tk.Label(self.parent, textvariable=self.servo_string, 
                               font=('Fixed', 14))
	self.lServo.grid(row=2, column=0, sticky=tk.W, columnspan=4)

	# Listbox holds the recordings
	self.listbox1 = tk.Listbox(self.parent, width=50, height=6)
	self.listbox1.grid(row=3, column=0, columnspan=8)
	self.listbox1.dir = './recordings/'

	# With a scrollbar
	self.yscroll = tk.Scrollbar(self.parent, command=self.listbox1.yview, 
                                    orient=tk.VERTICAL)
	self.yscroll.grid(row=3, column=8, sticky=tk.N+tk.S)
	self.listbox1.configure(yscrollcommand=self.yscroll.set)

        # Toggle stopwatch
        self.bStartStop = tk.Button(self.parent, 
                                    textvariable=self.startstop_string, 
                                    command=self.toggle)
        self.bStartStop.grid(row=4, column=0, sticky=tk.W)

        # Reload the list of recordings
	self.bList = tk.Button(self.parent, text='List', command=self.ListFiles())
	self.bList.grid(row=4, column=1, sticky=tk.W)    

        # Quit button
        self.bQuit = tk.Button(self.parent, text="Quit", 
                               fg="red", command=self.Quit)
        self.bQuit.grid(row=4, column=7, sticky=tk.W)

        # Initialize the things
        self.LoadIniData()
        self.ListFiles()
        self.storage_list = list()
        self.joymap = [3,4,1,2] # link between joystick and the servo to move
        self.joyreverse = [0,1,0,0,0]

    # Toggle stopwatch state
    def toggle(self):
        if self.stopwatch.running:
            self.startstop_string.set("Start")
        else:
            self.storage_list = list() #empty this out
            self.startstop_string.set("Stop")
        self.stopwatch.toggle(self.time_string, self.microseconds)

    def Quit(self):
        self.stopwatch.stop(self.time_string, self.microseconds)
        self.parent.quit()

    def LoadIniData(self):
        FileName = re.sub(r'\.py$', "", os.path.abspath( __file__ )) + '.ini'
        self.cp=ConfigParser()
        try:
            self.cp.readfp(open(FileName,'r'))
	# f.close()
        except IOError:
            raise Exception,'NoFileError'
        return

    def process_bits(self,rows):
        # this removes duplicates, easy. 
        rows = [ key for key,_ in groupby(rows)]
        l = {}
        for i in range(0,len(rows)):
            l[i] = {}
            t, l[i]['pos_str'] = rows[i].split(' ', 1)
            seconds, useconds = t.split(':')
            l[i]['time'] = float("%2.6lf" % float(seconds + "." + useconds))

        pos_old = l[0]['pos_str']
        t_old = l[0]['time']
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

    def PlayBack(self):
        bits = self.storage_list
        if len(bits) == 0:
            print "nothing recorded"
        else:
            bits = self.process_bits(bits)
            for i in range(0,len(bits)):
                servo, angle = bits[i]['pos_str'].split()
                print bits[i]['delta']
                time.sleep(bits[i]['delta'])
                self.ServoMove(int(servo), int(angle))

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

    def ListFiles(self):
        tk = Tkinter
        # delete contents of present listbox
        dir = self.listbox1.dir
        self.listbox1.delete(0, tk.END)
        dirlist = os.listdir(dir)
        for file in dirlist:
            if os.path.isfile(dir + file):
                fin = open(dir + file, "r")
                for line in fin.readlines():
                    name = line.rstrip('\n') + " :: " + file
                    break
                self.listbox1.insert(tk.END, name)
        return

if __name__ == "__main__":
    usbport = '/dev/ttyUSB0'
    # Set up serial baud rate
    ser = serial.Serial(usbport, 9600, timeout=1)
    tk = Tkinter.Tk()
    watch = recorder_handlers.Stopwatch()
    tkwin = tk_layout(tk, watch, ser)
    recorder_handlers.Joystick(tkwin)
    tk.mainloop()
