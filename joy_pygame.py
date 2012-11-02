#!/usr/bin/env python

import pygame
import serial

# com6 /dev/ttyS6
usbport = '/dev/ttyUSB0'

# Set up serial baud rate
ser = serial.Serial(usbport, 9600, timeout=1)

# Define some colors
black = ( 0, 0, 0)
white = ( 255, 255, 255)
green = ( 0, 255, 0)
red = ( 255, 0, 0)
y_inc = 20

info = {}
info[1] = {}
info[1]['reverse'] = 0
info[1]['center'] = 90
info[2] = {}
info[2]['reverse'] = 0
info[2]['center'] = 90
info[3] = {}
info[3]['reverse'] = 0
info[4] = {}
info[4]['reverse'] = 0

def servo_move(servo, angle):
    if (0 <= angle <= 180):
        ser.write(chr(255))
        ser.write(chr(servo))
        ser.write(chr(angle))
    else:
        print "Servo angle must be an integer between 0 and 180.\n"

def render_screen(screen,x1,y1,x2,y2):
	pygame.draw.ellipse(screen,black,[1+x1,y1,10,10],0)
	pygame.draw.ellipse(screen,red,  [1+x2,y2,10,10],0)
	xlabel1 = myfont.render(str(x1), 1, black)
	ylabel1 = myfont.render(str(y1), 1, black)
	xlabel2 = myfont.render(str(x2), 1, black)
	ylabel2 = myfont.render(str(y2), 1, black)
	screen.blit(xlabel1, (10, y_inc * 1))
	screen.blit(ylabel1, (10, y_inc * 2))
	screen.blit(xlabel2, (10, y_inc * 3))
	screen.blit(ylabel2, (10, y_inc * 4))
	pygame.init()

screen=pygame.display.set_mode([200,100])
pygame.display.set_caption("Recorder")
done=False
clock=pygame.time.Clock()

pygame.font.init()
myfont = pygame.font.SysFont("Comic Sans MS", 30)

# show the whole thing
pygame.display.flip()

# Count the joysticks the computer has
pygame.joystick.init()
pygame.display.init()
joystick_count=pygame.joystick.get_count()

if joystick_count == 0:
	print ("Error, I didn't find any joysticks.")
else:
	my_joystick = pygame.joystick.Joystick(0)
	my_joystick.init()

while done==False:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done=True

	if joystick_count != 0:
                x1 = int(90 + round(my_joystick.get_axis(0) * 90, 0))
		x1 = 180 - x1
                y1 = int(90 + round(my_joystick.get_axis(1) * 90, 0))

                x2 = int(90 + round(my_joystick.get_axis(2) * 90, 0))
                y2 = int(90 + round(my_joystick.get_axis(3) * 90, 0))

                servo_move(1, x1)
                servo_move(2, y1)
                servo_move(3, x2)
                servo_move(4, y2)

	screen.fill(white)
	render_screen(screen,x1,y1,x2,y2)
	pygame.display.flip()
	clock.tick(40)

pygame.quit ()
