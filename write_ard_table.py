#!/usr/bin/env python

import shutil
import pickle

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

def main():
    r = RecordingData("recordings.txt")
    count = 0

    names = ('r1', 'r2', 'r3', 'r4', 'r5')

    count = 0
    lengths = []
    for name in names:
        data = r.get_data(name)
        count += len(data) * 3
        lengths.append(len(data) * 3)

    print "#include <avr/pgmspace.h>\n"

    print "prog_uint16_t servoArrayLengths[%d] PROGMEM = {" % (len(lengths) * 2)
    x = lengths.pop()
    y = 0
    for l in lengths:
        print "%d, %d," % (y, int(l + y) - 3)
        y += l
    print "%d, %d\n};\n" % (y, x + y)

    print "prog_uint16_t servoArray[%d] PROGMEM = {" % count
    count = 0
    for name in names:
        data = r.get_data(name)
        row_count = 0
        time = 0;
        last_time = 0;
        for row in data:
            (i, j) = row.split(':')
            (k,m,n) = j.split(' ')
            k = int(float(k) * .001)
            time = (int(i) * 1000) + k
            time = time - last_time
            if (count == len(names) - 1 and row_count == len(data) - 1):
                print "%d,%d,%d" % (time, int(m), int(n))
            else:
                print "%d,%d,%d," % (time, int(m), int(n))
            last_time = (int(i) * 1000) + k
            row_count += 1
        count += 1
    print "};"

if __name__ == "__main__":
    main()
