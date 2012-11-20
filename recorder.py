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
        self.time_string = tk.StringVar(value="00:000000")
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
        self.listbox1.bind('<Double-Button-1>', self.onDouble)

	# With a scrollbar
	self.yscroll = tk.Scrollbar(self.parent, command=self.listbox1.yview, 
                                    orient=tk.VERTICAL)
	self.yscroll.grid(row=3, column=8, sticky=tk.N+tk.S)
	self.listbox1.configure(yscrollcommand=self.yscroll.set)

        # use entry widget to display/edit selection
        self.enter1 = tk.Entry(self.parent, width=40, bg='yellow')
        self.enter1.grid(row=4, column=0, sticky=tk.W, columnspan=6)
        self.enter1.bind('<Return>', self.onReturn)

        # Toggle stopwatch
        self.bStartStop = tk.Button(self.parent, 
                                    textvariable=self.startstop_string, 
                                    command=self.toggle)
        self.bStartStop.grid(row=5, column=0, sticky=tk.W)

        # Save file
        self.bSave = tk.Button(self.parent, 
                               text='Save',
                               command=self.SaveRecording)
        self.bSave.grid(row=5, column=1, sticky=tk.W)

        # Reload the list of recordings
	self.bDelete = tk.Button(self.parent, text='Delete', 
                               command=self.DeleteRecording)
	self.bDelete.grid(row=5, column=2, sticky=tk.W)    

        # Quit button
        self.bQuit = tk.Button(self.parent, text="Quit", 
                               fg="red", command=self.Quit)
        self.bQuit.grid(row=5, column=7, sticky=tk.W)

        self.ListRecordings()
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

    def UpCurser(self):
        print "upcurser"

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
        name = self.listbox1.get(index)
        # delete previous text in enter1
        self.enter1.delete(0, 50)
        # now display the selected text
        self.enter1.insert(0, name)
        # got the name, now fish it out of recording structure
        # and load into storage buffer
        self.storage_list = self.rdata.get_data(name)

    def SaveRecording(self):
        bits = self.storage_list
        name = self.enter1.get()
        if len(name) == 0:
            print "pick a name"
        else: 
            if len(bits) == 0:
                print "no recording, not saving"
            else:
                if self.rdata.get_data(name) == 0:
                    self.rdata.add(name, self.storage_list)
                else:
                    if (tkMessageBox.askokcancel(title="Save", \
                           message='Overwrite ' + name + '?') == 1):
                        self.rdata.remove(name)
                        self.rdata.add(name, self.storage_list)

        self.ListRecordings()

    def DeleteRecording(self):
        name = self.enter1.get()
        if len(name) == 0:
            print "pick a name"
        if (tkMessageBox.askokcancel(title="Delete", \
                           message='Delete ' + name + '?') == 1):
            self.rdata.remove(name)

        self.ListRecordings()

    def ListRecordings(self):
        tk = Tkinter
        # delete contents of present listbox
        # dir = self.listbox1.dir
        self.listbox1.delete(0, tk.END)
        l = self.rdata.get_names()
        for i in l:
            self.listbox1.insert(tk.END, i)
        self.SortList()

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

    def onDouble(self,event):
        self.PlayBack()

    def onReturn(self,event):
        self.SaveRecording()

    def PlayBack(self):
        if len(self.storage_list) != 0:
            bits = self.storage_list
        elif len(self.enter1.get()) != 0:
            name = self.enter1.get()
            self.storage_list = self.rdata.get_data(name)
            bits = self.storage_list
        else:
            print "nothing to play"
        if len(bits) != 0:
            bits = self.ProcessBits(bits)
            self.ServoCenter()
            counter = 0
            for i in range(0,len(bits)):
                servo, angle = bits[i]['pos_str'].split()
                counter = counter + bits[i]['delta']
                self.DisplayCounter(counter)
                time.sleep(bits[i]['delta'])
                self.ServoMove(int(servo), int(angle))

    def DisplayCounter(self,t): 
        t = str(t)
        (seconds, mseconds) = t.split('.')
        self.time_string.set("%02i:%06i" % (int(seconds), int(mseconds)))
        
    def ServoCurrentPos(self):
        s = self.servo_string
        t = re.sub(r'  *'," ",re.sub(r'^ *',"",s.get()))
        (s1, s2, s3, s4) = t.split(' ')
        return(int(s1), int(s2), int(s3), int(s4))
        
    def ServoSlowMove(self, a2, b2, c2, d2, inc):
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

    def ServoCenter(self):
        self.ServoSlowMove(90,90,90,90,40)

    def ServoMove(self,servo, angle):
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

    def ServoLoadString(self,num,pos):
        s = self.servo_string
        pos = '%3s' % (pos)
        t = re.sub(r'^ *',"",s.get())
        t = re.sub(r'  *'," ",t)
        pos = re.sub(r' '," ",pos)
        words = t.split(' ')
        str = ""
        for i in range(0, 4):
        	if (i == num):
        		x = '%3s' % pos
        	else:
        		x = '%3s' % words[i]
        	x = re.sub(r' ',"0",x)
        	str = str + x + ' '
        str = re.sub(r' *$',"",str)
        s.set(str)
        # needed because some times this is called out of main()
        self.parent.update_idletasks()

def main():
    tk = Tkinter.Tk()
    tkwin = app_setup(tk)
    tk.mainloop()

if __name__ == "__main__":
    main()
