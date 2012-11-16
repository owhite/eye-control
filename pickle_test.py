#!/usr/bin/env python

import pickle
from random import randint

class recording_data(object):
    def __init__(self, file_name):
        self.file = file_name
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

    def retreive(self, n):
        l = pickle.load(open(self.file, "rb"))
        r = 0
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

    def remove(self, n):
        l = pickle.load(open(self.file, "rb"))
        r = self.retreive(n)
        if r:
            new = {}
            count = 0
            for i in l:
                if i != r:
                    new[count] = {} 
                    new[count]['name'] = l[i]['name']
                    new[count]['data'] = l[i]['data']
                    count = count + 1
        pickle.dump(new, open(self.file, "wb"))

def make_fake_recording():
    l = []
    for i in range(2,randint(2,100)):
        s = '%d %d' % (randint(1,4), randint(0,180))
        l.extend([s])
    return l

def make_fake_list(self, inc):
    for i in range(2,inc):
        data = make_fake_recording()
        self.add('thing%d' % i, data)

def main():
    r = recording_data("r_file.txt")
    l = make_fake_list(r,10)
    l = r.get_names()
    for i in l:
        print i
    print 'remove thing 8'
    inc = r.remove('thing8')
    l = r.get_names()
    for i in l:
        print i

if __name__ == "__main__":
    main()
