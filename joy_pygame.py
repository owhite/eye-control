#!/usr/bin/env python

import pygame
import serial

# com6 /dev/ttyS6
usbport = '/dev/ttyUSB0'

# Set up serial baud rate
ser = serial.Serial(usbport, 9600, timeout=1)

def servo_move(servo, angle):
    if (0 <= angle <= 180):
        ser.write(chr(255))
        ser.write(chr(servo))
        ser.write(chr(angle))
    else:
        print "Servo angle must be an integer between 0 and 180.\n"

