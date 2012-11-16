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

# Handles the layout of the root window and lots of other stuff
class app_setup:
    def __init__(self, parent):
        parent.title("recorder")
        self.parent = parent
        tk = Tkinter

        # Initialize the things
        self.LoadIniData()
        usbport = self.cp.get('Variables', 'usbport')
        self.ser = serial.Serial(usbport, 9600, timeout=1)
        f = self.cp.get('Variables', 'recording_file')

        self.stopwatch = recorder_handlers.Stopwatch()
        self.rdata = recorder_handlers.RecordingData(f)

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
        self.listbox1.bind('<ButtonRelease-1>', self.GetList)

	# With a scrollbar
	self.yscroll = tk.Scrollbar(self.parent, command=self.listbox1.yview, 
                                    orient=tk.VERTICAL)
	self.yscroll.grid(row=3, column=8, sticky=tk.N+tk.S)
	self.listbox1.configure(yscrollcommand=self.yscroll.set)

        # use entry widget to display/edit selection
        self.enter1 = tk.Entry(self.parent, width=40, bg='yellow')
        self.enter1.grid(row=4, column=0, sticky=tk.W, columnspan=6)

        # pressing the return key will update edited line
        self.enter1.bind('<Return>', self.SetList)

        # Toggle stopwatch
        self.bStartStop = tk.Button(self.parent, 
                                    textvariable=self.startstop_string, 
                                    command=self.toggle)
        self.bStartStop.grid(row=5, column=0, sticky=tk.W)

        # Save file
        self.bSave = tk.Button(self.parent, 
                               text='Save',
                               command=self.SaveFile)
        self.bSave.grid(row=5, column=1, sticky=tk.W)

        # Reload the list of recordings
	self.bList = tk.Button(self.parent, text='List', 
                               command=self.ListFiles)
	self.bList.grid(row=5, column=2, sticky=tk.W)    

        # Quit button
        self.bQuit = tk.Button(self.parent, text="Quit", 
                               fg="red", command=self.Quit)
        self.bQuit.grid(row=5, column=7, sticky=tk.W)

        self.ListFiles()
        self.storage_list = list()
        self.joymap = [3,4,1,2] # link between joystick and the servo to move
        self.joyreverse = [0,1,0,0,0]

        recorder_handlers.Joystick(self)


    # Toggle stopwatch state
    def toggle(self):
        if self.stopwatch.running:
            self.startstop_string.set("Start")
        else:
            self.storage_list = list() #empty this out
            self.startstop_string.set("Stop")
        self.stopwatch.toggle(self.time_string, self.microseconds)

    def SetList(self, event):
        # inserts an edited line 
        try:
            index = self.listbox1.curselection()[0]
            # delete old listbox line
            self.listbox1.delete(index)
        except IndexError:
            index = tk.END
        # insert edited item back into listbox1 at index
        self.listbox1.insert(index, self.enter1.get())

    def SortList(self):
        tk = Tkinter
        temp_list = list(self.listbox1.get(0, tk.END))
        temp_list.sort(key=str.lower)
        # delete contents of present listbox
        self.listbox1.delete(0, tk.END)
        # load listbox with sorted data
        for item in temp_list:
            self.listbox1.insert(tk.END, item)

    # user selected something in listbox, move the name to entry widget
    def GetList(self, event):
        index = self.listbox1.curselection()[0]
        # get the line's text
        seltext = self.listbox1.get(index)
        # delete previous text in enter1
        self.enter1.delete(0, 50)
        # now display the selected text
        self.enter1.insert(0, seltext)

    def SaveFile(self):
        print "saving private file"
        bits = self.storage_list
        name = self.enter1.get()
        if len(name) == 0:
            print "pick a name"
        else: 
            if len(bits) == 0:
                print "no recording, not saving"
            else:
                fpath = self.cp.get('Variables', 'recording_dir') + name
                print fpath
                with open(fpath, 'w') as file:
                    file.write('[' + name + ']' + '\n')
                    for i in range(0,len(bits)):
                        print bits[i]
                        file.write(bits[i] + '\n')
                    file.close()
                self.ListFiles()

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
            bits = self.ProcessBits(bits)
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
        # dir = self.listbox1.dir
        self.listbox1.delete(0, tk.END)
        l = self.rdata.get_names()
        for i in l:
            print i
            self.listbox1.insert(tk.END, i)
        self.SortList()


def main():
    tk = Tkinter.Tk()
    tkwin = app_setup(tk)
    tk.mainloop()

if __name__ == "__main__":
    main()
