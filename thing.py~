#!/usr/bin/env python

import serial

# com6 /dev/ttyS6
usbport = '/dev/ttyUSB0'

# Set up serial baud rate
ser = serial.Serial(usbport, 9600, timeout=1)

print "\n================================================"
print "        Arduino/Python Servo Controller"
print "================================================"

try:
	import pygame.joystick
except:
	print "\nPlease install the 'pygame' module <http://www.pygame.org/>.\n"
	quit()

# Allow for multiple joysticks
joy = []

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



# Handle joystick event
def handleJoyEvent(e):
    # Identify joystick axes and assign events
    if e.type == pygame.JOYAXISMOTION:
        axis = "unknown"
        if (e.dict['axis'] == 0):
            axis = "X"
        if (e.dict['axis'] == 1):
            axis = "Y"
        if (e.dict['axis'] == 2):
            axis = "pupil_left_right"
        if (e.dict['axis'] == 3):
            axis = "pupil_up_down"

        # Convert joystick value to servo position for each axis
        if (axis != "unknown"):
            str = "Axis: %s; Value: %f" % (axis, e.dict['value'])
            # Uncomment to display axis values:

            # X Axis
            if (axis == "X"):
                pos = e.dict['value']
                # convert joystick position to servo increment, 0-180
                move = round(pos * 90, 0)
                serv = int(90 + move)
                # and send to Arduino over serial connection
                servo_move(3, serv)
		# print "x %lf %d" % (pos, serv)

            # Y Axis
            if (axis == "Y"):
                pos = e.dict['value']
                move = round(pos * 90, 0)
                serv = int(90 + move)
                servo_move(4, serv)
		# print "y %lf %d" % (pos, serv)
            # Z Axis
            if (axis == "pupil_up_down"):
                pos = e.dict['value']
                move = round(pos * 90, 0)
                serv = int(90 + move)
                servo_move(2, serv)
            # eyeball moves left
            if (axis == "pupil_left_right"):
                pos = e.dict['value']
                move = round(pos * 90, 0)
                serv = int(90 + move)
		# print "x %lf %d" % (pos, serv)
                servo_move(1, serv)

    # Assign actions for Button DOWN events
    elif e.type == pygame.JOYBUTTONDOWN:
        # Button 1 (trigger)
        if (e.dict['button'] == 0):
            print "Exiting"
            quit()
        # Button 2
        if (e.dict['button'] == 1):
            print "Button 2 Down"
        # Button 3
        if (e.dict['button'] == 2):
            print "Button 3 Down"
        # Button 4
        if (e.dict['button'] == 3):
            print "Button 4 Down"
        # Button 5
        if (e.dict['button'] == 4):
            print "Button 5 Down"
        # Button 6
        if (e.dict['button'] == 5):
            print "Button 6 Down"

    # Assign actions for Button UP events
    elif e.type == pygame.JOYBUTTONUP:
        # Button 1 (trigger)
        if (e.dict['button'] == 0):
            print "Trigger Up"
        # Button 2
        if (e.dict['button'] == 1):
            print "Button 2 Up"
        # Button 3
        if (e.dict['button'] == 2):
            print "Button 3 Up"
        # Button 4
        if (e.dict['button'] == 3):
            print "Button 4 Up"
        # Button 5
        if (e.dict['button'] == 4):
            print "Button 5 Up"
        # Button 6
        if (e.dict['button'] == 5):
            print "Button 6 Up"

    # Assign actions for Coolie Hat Switch events
    elif e.type == pygame.JOYHATMOTION:
        if (e.dict['value'][0] == -1):
            print "Hat Left"
            servo_move(4, 0)
        if (e.dict['value'][0] == 1):
            print "Hat Right"
            servo_move(4, 180)
        if (e.dict['value'][1] == -1):
            print "Hat Down"
        if (e.dict['value'][1] == 1):
            print "Hat Up"
        if (e.dict['value'][0] == 0 and e.dict['value'][1] == 0):
            print "Hat Centered"
            servo_move(4, 90)
		
    else:
        pass

def servo_move(servo, angle):
    if (info[servo]['reverse'] == 1):
	angle = 180 - (angle - 90)
    if (0 <= angle <= 180):
        ser.write(chr(255))
        ser.write(chr(servo))
        ser.write(chr(angle))
    else:
        print "Servo angle must be an integer between 0 and 180.\n"

# Print the joystick position
def output(line, stick):
    print "Joystick: %d; %s" % (stick, line)

# Wait for joystick input
def joystickControl():
    while True:
        e = pygame.event.wait()
        if (e.type == pygame.JOYAXISMOTION or e.type == pygame.JOYBUTTONDOWN or e.type == pygame.JOYBUTTONUP or e.type == pygame.JOYHATMOTION):
            handleJoyEvent(e)

# Main method
def main():
    # Initialize pygame
    pygame.joystick.init()
    pygame.display.init()
    if not pygame.joystick.get_count():
        print "\nPlease connect a joystick and run again.\n"
        quit()
    print "\n%d joystick(s) detected." % pygame.joystick.get_count()
    for i in range(pygame.joystick.get_count()):
        myjoy = pygame.joystick.Joystick(i)
        myjoy.init()
        joy.append(myjoy)
        print "Joystick %d: " % (i) + joy[i].get_name()
    print "Depress joystick button 1 to quit.\n"

    servo_move(1, info[1]['center'])
    servo_move(2, info[2]['center'])

    # Run joystick listener loop
    joystickControl()

# Allow use as a module or standalone script
if __name__ == "__main__":
    main()
