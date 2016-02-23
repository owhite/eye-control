#!/usr/bin/env python

a = [10,10,10]

y = 0
t = 0
for x in a:
    print ("%d, %d") % (y, x - 1 + y)
    y += x
