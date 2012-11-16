#!/usr/bin/env python

import Tkinter
from Tkinter import *
import pygame
import time

class Find_Joystick:
	def __init__(self, root):
		self.root = root

		## initialize pygame and joystick
		pygame.init()
		if(pygame.joystick.get_count() < 1):
			# no joysticks found
			print "Please connect a joystick.\n"
			self.quit()
		else:
			# create a new joystick object from
			# ---the first joystick in the list of joysticks
			Joy0 = pygame.joystick.Joystick(0)
			# tell pygame to record joystick events
			Joy0.init()

		## bind the event I'm defining to a callback function
		self.root.bind("<<JoyFoo>>", self.my_event_callback)

		## start looking for events
		self.root.after(0, self.find_events)

	def find_events(self):
		## check everything in the queue of pygame events
		events = pygame.event.get()
		for event in events:
			# event type for pressing any of the joystick buttons down
			if event.type == pygame.JOYBUTTONDOWN:
				# generate the event I've defined
				self.root.event_generate("<<JoyFoo>>")

		## return to check for more events in a moment
		self.root.after(20, self.find_events)

	def my_event_callback(self, event):
		print "Joystick button press (down) event"

class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.initUI()
        
    def initUI(self):
        self.parent.title('Button')

        self.string = StringVar(value="time stuff")
        l1 = Label(self.parent, textvariable=self.string, font=('Fixed', 14))
        l1.grid(row=1, column=0, sticky=W, columnspan=4)

        self.bStop = Button(self.parent, text="stop", command=self.quit)
        self.bStop.grid(row=2, column=0, sticky=W)

        self.bTime = Button(self.parent, text="time", command=self.thing)
        self.bTime.grid(row=2, column=2, sticky=W)

    def quit(self):
        import sys
        sys.exit()

    def thing(self):
        self.string.set(time.time())

def main():
    root = Tk()
    ui_setup = Example(root)
    app = Find_Joystick(root)
    root.mainloop()  

if __name__ == '__main__':
    main()  
