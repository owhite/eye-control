#!/usr/bin/env python

from itertools import groupby

def process_bits(rows):
    # this removes duplicates, easy. 
    rows = [ key for key,_ in groupby(rows)]

    l = {}
    for i in range(0,len(rows)):
        l[i] = {}
	t, l[i]['pos_str'] = rows[i].split(' ', 1)
	seconds, useconds = t.split(':')
	l[i]['time'] = float("%2.6lf" % float(seconds + "." + useconds))

    pos_old = l[0]['pos_str']
    t_old = l[0]['time']
    new = {}
    count = 0
    for i in range(1,len(rows)):
        pos = l[i]['pos_str']
        t = l[i]['time']
	if pos != pos_old:
           new[count] = {}
           new[count]['delta'] = str(l[i]['time']) + " - " + str(t_old)
           new[count]['pos_str'] = pos_old
	   pos_old = pos
	   t_old = t
	   count = count + 1
    new[count] = {}
    new[count]['delta'] = str(l[i]['time']) + " - " + str(t_old)
    new[count]['pos_str'] = pos_old
    return new

def main():
    lines = [line.strip() for line in open("tmp.txt", 'r')]
    lines = process_bits(lines)
    for i in range(0,len(lines)):
	    print lines[i]['delta'] + ' ' + lines[i]['pos_str']

if __name__ == "__main__":
    main()
