#!/usr/bin/env python

import pickle
from random import randint

class recording(object):
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
            self.l[i] = {} 
            self.l[i]['name'] = 'thing%d' % i
            self.l[i]['data'] = data

    def dump_list(self):
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
    r = recording()
    l = r.make_fake_list(10)
    r.dump_list()
    inc = r.remove('thing8')
    r.dump_list()

if __name__ == "__main__":
    main()
