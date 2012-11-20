from threading import Thread

import shutil
import time, datetime
import pygame
import re
import sys
import pickle

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

class Joystick:
    def __init__(self, root):
        self.root = root
    	## initialize pygame and joystick

    	pygame.init()
    	if(pygame.joystick.get_count() < 1):
    		# no joysticks found
    		print "Please connect a joystick.\n"
    		self.Quit()
    	else:
    		# create joystick object from first joystick in list
    		Joy0 = pygame.joystick.Joystick(0)
    		Joy0.init()

    	## all this call back stuff makes no sense to me. 
        self.root.parent.bind("<<JoyFoo>>", self.my_event_callback)
    	## start looking for events
        self.root.parent.after(0, self.find_events)

    def find_events(self):
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN:
                # generate the event I've defined
                # self.root.event_generate("<<JoyFoo>>")
                # print e.dict['button']
                if (e.dict['button'] == 5):
                    self.root.toggle()
                if (e.dict['button'] == 7):
                    self.root.PlayBack()
            if e.type == pygame.JOYAXISMOTION:
                pos = e.dict['value']
                pos = int(90 + round(pos * 90, 0))
                n = e.dict['axis']
                if (n >= 0 and n < 5):
                    # constructs the string that reflects joystick
                    #  position
                    self.root.ServoMove(n,pos)
                    if self.root.stopwatch.running: 
                        thing = "%s %d %d" % (self.root.time_string.get(), 
                                           n, pos)
                        self.root.storage_list.append(thing)

        ## return to check for more events in a moment
        self.root.parent.after(20, self.find_events)

    # I dont know what this does.
    def my_event_callback(self, event):
        print "Joystick button press (down) event"

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

