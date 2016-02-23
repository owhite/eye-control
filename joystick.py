#!/usr/bin/env python

# This is a truncated form of: http://www.pygame.org/docs/ref/joystick.html

import pygame
import serial

## initialize pygame and joystick
#   make sure your gamepad is plugged in
pygame.init()
if(pygame.joystick.get_count() < 1):
    print "Please connect a joystick.\n"
    sys.exit()
else:
    Joy0 = pygame.joystick.Joystick(0)
    Joy0.init()

## initialize serial connection to arduino
# be sure to figure out how where you 
serial_exists = 0
usbport = '/dev/tty.usbmodem226331'
try:
    serial = serial.Serial(usbport, 115200)
    serial_exists = 1
except:
    print "   did you plug something into " + usbport + "?"

done = False

while done==False:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.JOYBUTTONDOWN:
            if (e.dict['button'] == 5):
                print "user pushed button %d" % e.dict['button']
            if (e.dict['button'] == 7):
                print "user pushed button %d, exiting" % e.dict['button']
                done = True;
        if e.type == pygame.JOYAXISMOTION:
            pos = e.dict['value']
            pos = int(90 + round(pos * 90, 0))
            n = e.dict['axis']
            if (n >= 0 and n < 5):
                print "sending servo:%d :: angle:%d" % (n, pos)
                if (serial_exists):
                    serial.write("%d %d" % (n+1, pos))
