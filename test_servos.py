#!/usr/bin/env python

# to supress noise on the command line
#  defaults write org.python.python ApplePersistenceIgnoreState NO

import os
import re
import sys
import time, datetime
import serial
from itertools import groupby
import tkMessageBox
from ConfigParser import *
import shutil
import pygame
import pickle
from threading import Thread

from Tkinter import *

# Handles the layout of the root window and lots of other stuff
class app_setup:
    def __init__(self, root):

        self.LoadIniData()
        self.serial_exists = 0
        usbport = self.cp.get('Variables', 'usbport')
        try:
            self.serial = serial.Serial(usbport, 115200)
            self.serial_exists = 1
        except:
            print "   did you plug something into " + usbport + "? an eyeball for example?"

        self.root = root
        root.wm_title("Eye Control")

        self.stopwatch = Stopwatch()
        f = self.cp.get('Variables', 'recording_file')
        self.rdata = RecordingData(f)

        self.canvasWidth = 300
        self.centerWidth = self.canvasWidth / 2
        centerW = self.centerWidth

        self.canvasHeight = 200
        self.centerHeight = self.canvasHeight / 2
        centerH = self.centerHeight

        canvas = Canvas(root,
                        width=self.canvasWidth,
                        height = self.canvasHeight)

        self.canvas = canvas

        canvas.grid(column=0, row=0, columnspan=4)

        self.irisW = 40
        self.irisH = 40
        self.irisPosition = (self.angleRange(90,1),
                             self.angleRange(90,1))

        self.iris = canvas.create_oval(centerW - self.irisW / 2,
                                       centerH - self.irisH / 2,
                                       centerW + self.irisW / 2,
                                       centerH + self.irisH / 2,
                                       outline='white', fill='blue')

        self.lidTopPosition = (self.angleRange(90,1),
                               self.angleRange(90,1))

        self.lidTopWidth = 200
        self.lidTop = canvas.create_line(centerW - self.lidTopWidth/2,
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

        # Current time
        self.startstop_string = StringVar(value="Start")
        self.time_string = StringVar(value="00:000000")
        self.microseconds = 0
        self.lTime = Label(root, textvariable=self.time_string, 
                           font=('Fixed', 14))
        self.lTime.grid(row=1, column=0, columnspan=4)

        self.joystick_position = [90,90,90,90]
        self.joystick_string = StringVar(value="090 090 090 090")
	self.lJoystick = Label(root,
                               textvariable=self.joystick_string, 
                               font=('Fixed', 14))
	self.lJoystick.grid(row=2, column=0, columnspan=4)

        self.servo_position = [90,90,90,90]
        self.mapServoPositions()
        self.servo_string = StringVar(value="090 090 090 090")
	self.lServo = Label(root,
                            textvariable=self.servo_string, 
                            font=('Fixed', 14))
	self.lServo.grid(row=3, column=0, columnspan=4)


	# Listbox holds the recordings
	self.listbox1 = Listbox(root, width=50, height=6)
	self.listbox1.grid(row=4, column=0, columnspan=4, padx=5)
        self.listbox1.bind('<ButtonRelease-1>', self.GetList)
        self.listbox1.bind('<Double-Button-1>', self.onDouble)

	# With a scrollbar
	self.yscroll = Scrollbar(root, command=self.listbox1.yview, 
                                    orient=VERTICAL)
	self.yscroll.grid(row=4, column=8, sticky=N+S)
	self.listbox1.configure(yscrollcommand=self.yscroll.set)

        # use entry widget to display/edit selection
        self.enter1 = Entry(root, width=40, bg='yellow')
        self.enter1.grid(row=5, column=0, columnspan=4)
        self.enter1.bind('<Return>', self.onReturn)

        # Toggle stopwatch
        self.bStartStop = Button(root, 
                                    textvariable=self.startstop_string, 
                                    command=self.toggle)
        self.bStartStop.grid(row=6, column=0)
        # , sticky=W)

        # Save file
        self.bSave = Button(root, 
                               text='Save',
                               command=self.SaveRecording)
        self.bSave.grid(row=6, column=1)

        # Reload the list of recordings
	self.bDelete = Button(root, text='Delete', 
                               command=self.DeleteRecording)
	self.bDelete.grid(row=6, column=2)

        # Quit button
        self.bQuit = Button(root, text="Quit", 
                               fg="red", command=self.Quit)
        self.bQuit.grid(row=6, column=3)

        self.ListRecordings()
        self.storage_list = list()
        self.joymap = [1,0,2,3] # link between joystick and the servo to move

        ## initialize pygame and joystick
        pygame.init()
        if(pygame.joystick.get_count() < 1):
            print "Please connect a joystick.\n"
            self.quit()
        else:
            Joy0 = pygame.joystick.Joystick(0)
            Joy0.init()

        self.root.bind("<<JoyFoo>>", self.my_event_callback)
        self.root.after(0, self.find_joystick_events)

    def find_joystick_events(self):
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN:
                if (e.dict['button'] == 5):
                    self.toggle()
                if (e.dict['button'] == 7):
                    self.PlayBack()
            if e.type == pygame.JOYAXISMOTION:
                pos = e.dict['value']
                pos = int(90 + round(pos * 90, 0))
                n = e.dict['axis']
                if (n >= 0 and n < 5):
                    self.JoystickUpdate(n, pos)
                    if self.stopwatch.running: 
                        thing = "%s %d %d" % (self.time_string.get(), n, pos)
                        self.storage_list.append(thing)
        self.root.after(20, self.find_joystick_events)

    def my_event_callback(self, event):
        print "Joystick button press (down) event"

    def angleRange(self, angle, factor):
        return(int(angle - 90 * factor))

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
            index = END
        # insert edited item back into listbox1 at index
        self.listbox1.insert(index, self.enter1.get())

    def SortList(self):
        temp_list = list(self.listbox1.get(0, END))
        temp_list.sort(key=str.lower)
        # delete contents of present listbox
        self.listbox1.delete(0, END)
        # load listbox with sorted data
        for item in temp_list:
            self.listbox1.insert(END, item)

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
        # delete contents of present listbox
        # dir = self.listbox1.dir
        self.listbox1.delete(0, END)
        l = self.rdata.get_names()
        for i in l:
            self.listbox1.insert(END, i)
        self.SortList()

    def Quit(self):
        self.stopwatch.stop(self.time_string, self.microseconds)
        self.root.destroy()

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
            return()

        if len(bits) != 0:
            bits = self.ProcessBits(bits)
            self.ServoCenter()
            counter = 0
            for i in range(0,len(bits)):
                servo, angle = bits[i]['pos_str'].split()
                servo = int(servo)
                angle = int(angle)
                counter = counter + bits[i]['delta']
                self.DisplayCounter(counter)
                time.sleep(bits[i]['delta'])
                self.servo_position[servo] = angle
                self.updateCanvas()
                self.root.update_idletasks()
                if (self.serial_exists):
                    self.serial.write("%d %d" % (servo+1, angle))

    def DisplayCounter(self,t): 
        t = str(t)
        (seconds, mseconds) = t.split('.')
        self.time_string.set("%02i:%06i" % (int(seconds), int(mseconds)))
        
    def JoystickUpdate(self, num, pos):
        self.joystick_position[num] = pos
        if (self.joystick_position[1] < self.joystick_position[0]):
            self.joystick_position[1] = self.joystick_position[0]
        self.mapServoPositions()
        self.updateCanvas()
        self.LoadStringServo()
        self.LoadStringJoystick()
        # pump result to servo
        if (self.serial_exists):
            self.serial.write("%d %d" % (num+1, self.servo_position[num]))

    def mapServoPositions(self):
        # no mapping was really needed
        self.servo_position[0] = self.joystick_position[0]
        self.servo_position[1] = self.joystick_position[1]
        self.servo_position[2] = self.joystick_position[2]
        self.servo_position[3] = self.joystick_position[3]

    def updateCanvas(self):
        self.updateLidTop()
        self.updateLidBottom()
        self.updateIris()

    def updateLidTop(self):
        new = self.servo_position[0] - 90
        (x, y) = self.lidTopPosition
        self.lidTopPosition = (x, new)
        self.canvas.move(self.lidTop, 0, new - y)

    def updateLidBottom(self):
        new = self.servo_position[1] - 90
        (x, y) = self.lidBottomPosition
        self.lidBottomPosition = (x, new)
        self.canvas.move(self.lidBottom, 0, new - y)

    def updateIris(self):
        newX = (180 - self.servo_position[2]) - 90
        newY = self.servo_position[3] - 90
        (x, y) = self.irisPosition
        self.irisPosition = (newX, newY)
        self.canvas.move(self.iris, newX - x, newY - y)

    def ServoCenter(self):
        self.ServoSlowMove(90,90,90,90,40)

    def ServoSlowMove(self, a2, b2, c2, d2, inc):
        (a1, b1, c1, d1) = self.servo_position
        i1 = float(a2 - a1) / inc
        i2 = float(b2 - b1) / inc
        i3 = float(c2 - c1) / inc
        i4 = float(d2 - d1) / inc
        for i in range(0, inc):
            self.servo_position[0] = int(float(a1) + i1)
            self.servo_position[1] = int(float(b1) + i2)
            self.servo_position[2] = int(float(c1) + i3)
            self.servo_position[3] = int(float(d1) + i4)
            self.updateCanvas()

    def LoadStringServo(self):
        s1 = re.sub(r' ', '0','%3d' % self.servo_position[0])
        s2 = re.sub(r' ', '0','%3d' % self.servo_position[1])
        s3 = re.sub(r' ', '0','%3d' % self.servo_position[2])
        s4 = re.sub(r' ', '0','%3d' % self.servo_position[3])
        self.servo_string.set(("%s %s %s %s") % (s1, s2, s3, s4))
        self.root.update_idletasks()

    def LoadStringJoystick(self):
        s1 = re.sub(r' ', '0','%3d' % self.joystick_position[0])
        s2 = re.sub(r' ', '0','%3d' % self.joystick_position[1])
        s3 = re.sub(r' ', '0','%3d' % self.joystick_position[2])
        s4 = re.sub(r' ', '0','%3d' % self.joystick_position[3])
        self.joystick_string.set(("%s %s %s %s") % (s1, s2, s3, s4))
        self.root.update_idletasks()


class Stopwatch:
    def __init__(self):
        """Initialize Stopwatch instance."""
        self.first_time = 0.
        self.curr_time = 0.
        self.running = False
        self.thread = None

    def start(self, string_var, msecs):
        """Spawn a new thread to start the stopwatch."""
        self.running = True
        self.first_time = datetime.datetime.now()
        self.thread = StopwatchThread(self, string_var, msecs)
        self.thread.start()

    def stop(self, string_var, msecs):
        """Stop the subthread to stop the stopwatch."""
        self.running = False
        if self.thread:
            self.thread._Thread__stop()
        self.first_time = 0.

    def toggle(self, string_var, msecs):
        """Toggle state of stopwatch."""
        if self.running:
            self.stop(string_var, msecs)
        else:
            self.start(string_var, msecs)

class StopwatchThread(Thread):
    """Thread for stopwatch counting."""
    def __init__(self, watch, string_var, msecs):
        """Initialize the StopwatchThread instance."""
        Thread.__init__(self)
        self.watch = watch
        self.string_var = string_var
        self.microseconds = msecs

    def run(self):
        """Main thread method."""
        while True:
            self.watch.curr_time = datetime.datetime.now()
            the_time = self.watch.curr_time - self.watch.first_time
            seconds = the_time.seconds%60
            t = "%02i:%06i" % (seconds, the_time.microseconds)
            self.string_var.set(t)
            self.microseconds = the_time.microseconds
            time.sleep(0.005)
            if not self.isAlive():
                break

class RecordingData:
    def __init__(self, file_name):
        self.file = file_name
        try:
            shutil.copyfile(self.file, self.file + ".bak")
            with open(self.file) as f: pass
            l = pickle.load(open(self.file, "rb"))
        except IOError as e:
            l = []
            l = {}
            pickle.dump(l, open(self.file, "wb"))

    def add(self, name, data):
        l = pickle.load(open(self.file, "rb"))
        i = len(l)
        l[i+1] = {} 
        l[i+1]['name'] = name
        l[i+1]['data'] = data
        pickle.dump(l, open(self.file, "wb"))

    def dump(self):
        l = pickle.load(open(self.file, "rb"))
        for i in l:
            print '%d %s' % (i, l[i]['name'])
            print l[i]['data']

    def index(self, n):
        l = pickle.load(open(self.file, "rb"))
        r = -1
        for i in l:
            if n == l[i]['name']:
                r = i
                break
        pickle.dump(l, open(self.file, "wb"))


        return(r)

    def get_names(self):
        l = pickle.load(open(self.file, "rb"))
        j = []
        for i in l:
            j.extend([l[i]['name']])
        return(j)

    def get_data(self,name):
        l = pickle.load(open(self.file, "rb"))
        r = 0
        for i in l:
            if l[i]['name'] == name:
                r = l[i]['data']
                break
        return(r)

    def remove(self, n):
        l = pickle.load(open(self.file, "rb"))
        print "kill " + n
        r = self.index(n)
        print r
        if r != -1:
            new = {}
            count = 0
            for i in l:
                if i != r:
                    new[count] = {} 
                    new[count]['name'] = l[i]['name']
                    new[count]['data'] = l[i]['data']
                    count = count + 1
            pickle.dump(new, open(self.file, "wb"))


def main():
    root = Tk()
    ap = app_setup(root)
    root.mainloop()

if __name__ == "__main__":
    main()
