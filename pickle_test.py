#!/usr/bin/env python

import pickle
from random import randint

class recording_data(object):
    def __init__(self):
        self.l = []

    def make_fake_recording(self):
        l = []
        for i in range(2,randint(2,100)):
            s = '%d %d' % (randint(1,4), randint(0,180))
            l.extend([s])
        return l

    def make_fake_list(self, inc):
        self.l = {}
        for i in range(2,inc):
            data = self.make_fake_recording()
            self.add('thing%d' % i, data)

    def add(self, name, data):
        i = len(self.l)
        self.l[i+1] = {} 
        self.l[i+1]['name'] = name
        self.l[i+1]['data'] = data

    def dump(self):
        for i in self.l:
            print '%d %s' % (i, self.l[i]['name'])
            print self.l[i]['data']

    def retreive(self, n):
        r = 0
        for i in self.l:
            if n == self.l[i]['name']:
                r = i
                break
        return(r)

    def get_names(self):
        l = []
        for i in self.l:
            l.extend([self.l[i]['name']])
        return(l)

    def remove(self, n):
        r = self.retreive(n)
        if r:
            new = {}
            count = 0
            for i in self.l:
                if i != r:
                    new[count] = {} 
                    new[count]['name'] = self.l[i]['name']
                    new[count]['data'] = self.l[i]['data']
                    count = count + 1
            self.l = []
            self.l = new

def main():
    r = recording_data()
    l = r.make_fake_list(10)
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
