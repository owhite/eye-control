#!/usr/bin/python
from Tkinter import *
from ConfigParser import *
import os
import re
import pygame
import sys

class Find_Joystick:
	def __init__(self, root):
		self.root = root

		## initialize pygame and joystick
		pygame.init()
		if(pygame.joystick.get_count() < 1):
			# no joysticks found
			print "Please connect a joystick.\n"
			self.Quit()
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
		for e in events:
			# event type for pressing any of the joystick buttons down
			if e.type == pygame.JOYBUTTONDOWN:
				# generate the event I've defined
				self.root.event_generate("<<JoyFoo>>")
			if e.type == pygame.JOYAXISMOTION:
				if (e.dict['axis'] == 0):
					pos = e.dict['value']
					x = '%3d' % (int(90 + round(pos * 90, 0)))
					self.root.servo1_x.insert(0,x)

				if (e.dict['axis'] == 1):
					pos = e.dict['value']
					y = '%3d' % (int(90 + round(pos * 90, 0)))
					self.root.servo1_y.insert(0,y)
				if (e.dict['axis'] == 2):
					pos = e.dict['value']
					x = '%3d' % (int(90 + round(pos * 90, 0)))
					self.root.servo2_x.insert(0,x)

				if (e.dict['axis'] == 3):
					pos = e.dict['value']
					y = '%3d' % (int(90 + round(pos * 90, 0)))
					self.root.servo2_y.insert(0,y)



		## return to check for more events in a moment
		self.root.after(20, self.find_events)

	def my_event_callback(self, event):
		print "Joystick button press (down) event"

class handlers:
	def __init__(self, root):
		self.root = root

	## quit out of everything
	def Quit(self):
		print "quiting...\n"
		sys.exit()

	def Record(self):
		sys.stdout.write("Cant record yet")
		sys.Quit()

	def SaveConfig(self):
		sys.stdout.write("TBD")
		sys.Quit()

	def LoadIniData(self, FileName):
		self.cp=ConfigParser()
		try:
			self.cp.readfp(open(FileName,'r'))
		# f.close()
		except IOError:
			raise Exception,'NoFileError'
		return

def main():
	## Tkinter initialization
	root = Tk()
	app = Find_Joystick(root)

	h = handlers(root)

	name = re.sub(r'\.py$', "", os.path.abspath( __file__ )) + '.ini'
	h.LoadIniData(name)

	root.protocol('WM_DELETE_WINDOW', h.Quit)
	# why doesnt this work?
	# root.bind('<Control-c>', h.Quit())

        root.sp1 = Label(root)
        root.sp1.grid(row=0)
        
        root.st02 = Label(root, text='s1 xpos')
        root.st02.grid(row=2, column=0, sticky=E)
        root.servo1_xVar = StringVar()
        root.servo1_x = Entry(root, width=3, textvariable=root.servo1_xVar)
        root.servo1_x.grid(row=2, column=1, sticky=W)
        
        root.st03 = Label(root, text='s2 ypos')
        root.st03.grid(row=2, column=2, sticky=E)
        root.servo1_yVar = StringVar()
        root.servo1_y = Entry(root, width=3, textvariable=root.servo1_yVar)
        root.servo1_y.grid(row=2, column=3, sticky=W)
        
        root.st04 = Label(root, text='s3 xpos')
        root.st04.grid(row=2, column=4, sticky=E)
        root.servo2_xVar = StringVar()
        root.servo2_x = Entry(root, width=3, textvariable=root.servo2_xVar)
        root.servo2_x.grid(row=2, column=5, sticky=W)
        
        root.st05 = Label(root, text='s4 ypos')
        root.st05.grid(row=2, column=6, sticky=E)
        root.servo2_yVar = StringVar()
        root.servo2_y = Entry(root, width=3, textvariable=root.servo2_yVar)
        root.servo2_y.grid(row=2, column=7, sticky=W)
        
        root.sp4 = Label(root)
        root.sp4.grid(row=8)
        
        root.RecButton = Button(root, text='Rec',command=h.Record)
        root.RecButton.grid(row=9, column=0, columnspan = 2)
        
        root.SaveButton = Button(root, text='Save',command=h.SaveConfig)
        root.SaveButton.grid(row=9, column=2, columnspan = 2)

        root.quitButton = Button(root, text='Quit', command=h.Quit)
        root.quitButton.grid(row=9, column=4, sticky=E)    

	root.mainloop()

if __name__ == "__main__":
	main()
