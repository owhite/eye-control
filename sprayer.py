# adapted from:
#  http://stackoverflow.com/questions/12643079/bezier-curve-fitting-with-scipy/14125828

import random
import numpy as np
from scipy.misc import comb
from collections import deque

class Bezier(object):
    def __init__(self):
        super(Bezier, self).__init__()
        pass

    # The Bernstein polynomial of n, i as a function of t
    def bernstein_poly(self, i, n, t): 
        return comb(n, i) * ( t**(n-i) ) * (1 - t)**i

    # Given a set of control points, return the bezier curve defined by the control points.
    # points should be a flat list
    # such as [1,1, 2,2,  3,3, ...Xn,Yn]
    # nTimes is the number of time steps, defaults to 1000
    def bezier_curve(self, points, nTimes=1000): 
        nPoints = len(points) / 2
        t = np.linspace(0.0, 1.0, nTimes)
        polynomial_array = np.array([self.bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)])

        nPoints *= 2

        l1 = []
        l2 = []
        for i in range(0, nPoints, 2): 
            l1.append(points[i])
            l2.append(points[i+1])

        xvals = np.dot(np.array(l1), polynomial_array)
        yvals = np.dot(np.array(l2), polynomial_array)

        l1 = []
        for i in range(0, nTimes, 2): 
            l1.append(xvals[i])
            l1.append(yvals[i+1])

        return l1

    def split_pairs(self,l):
        l1 = []
        l2 = []
        for i in range(0, len(l), 2): 
            l1.append(l[i])
            l2.append(l[i+1])
            
        return l1, l2

    def plot_points(self, plt, points):
        xpoints, ypoints = b.split_pairs(points) 
        plt.plot(xpoints, ypoints, "ro")
        for nr in range(len(xpoints)):
            plt.text(xpoints[nr], ypoints[nr], nr)

    def plot_line(self, plt, line):
        xvals, yvals = b.split_pairs(line)
        plt.plot(xvals, yvals)

    def plot_bezier_and_points(self, plt, points):
        b.plot_points(plt, points)
        bezier = b.bezier_curve(points, nTimes=1000)
        b.plot_line(plt, bezier)

class BubbleEmit(object):
    def __init__(self, angle=None, offsetx=None, offsety=None, length=None, num=None, bubble_size = None, steps = None):
        super(BubbleEmit, self).__init__()

    def update(self):
        step_inc = self.length / self.steps
        pos_inc = self.length / self.num
        pos = 0
        for i in range(len(self.queue)):
            bubble = self.queue[i]
            bubble['angle'] += (bubble['rvel'] * bubble['dir']) 
            bubble['angle'] = bubble['angle'] % 360
            bubble['pos'] += step_inc
            bubble['pt'] = self.get_point_on_line(self.get_point_on_axis(bubble['pos']), 
                                                  bubble['dia'], 
                                                  bubble['angle'])
            if bubble['pos'] > self.length:
                self.queue.pop(i) # retire that one
                # put a new one on the front
                self.queue = [self.create_bubble(pos)] + self.queue
                pos += pos_inc

    def create_bubble(self, pos):
        dir = random.choice([-1,1])
        dia = random.randrange(self.bubble_size / 3, self.bubble_size)
        rvel = random.randrange(12 / 3, 12)
        angle = random.randrange(60,120) * dir

        pt = self.get_point_on_line(self.get_point_on_axis(pos), dia, angle)

        return({'pos':pos, 'rvel':12, 'dir':dir, 'dia':dia, 'angle':angle, 'pt':pt})

    def start(self):
        self.check()
        inc = self.length / (self.num + 1)
        pos = inc
        self.queue = []
        for i in range(self.num):
            self.queue.append(self.create_bubble(pos))
            pos += inc
        
    def check(self):
        self.ready = True
        if self.angle==None:
            print 'need an angle'
            self.ready = False
        if self.offsetx==None:
            print 'need offsetx'
            self.ready = False
        if self.offsety==None:
            print 'need offsety'
            self.ready = False
        if self.length==None:
            print 'need length'
            self.ready = False
        if self.num==None:
            print 'need num'
            self.ready = False
        if self.bubble_size==None:
            print 'need bubble_size'
            self.ready = False
        if self.steps==None:
            print 'need steps'
            self.ready = False
        
    def get_point_on_line(self, pt, l, angle):
        (x, y) = pt
        x = x + (l * np.cos(np.radians(angle))) 
        y = y + (l * np.sin(np.radians(angle))) 
        return x, y

    def get_point_on_axis(self, l):
        return self.get_point_on_line((self.offsetx, self.offsety), l, self.angle)


if __name__ == '__main__':

    from matplotlib import pyplot as plt
    import numpy as np

    b = Bezier()

    be = BubbleEmit()

    be.offsetx = 10
    be.offsety = 10
    be.length = 200
    be.angle = 45
    be.bubble_size = 60
    be.num = 5
    be.steps = 200

    be.start()
    be.update()

    pt = be.get_point_on_axis(be.length)

    xpts = [be.offsetx, pt[0]]
    ypts = [be.offsety, pt[1]]
    plt.plot(xpts, ypts, '-')

    l = []
    l.append(be.offsetx)
    l.append(be.offsety)
    for bubble in be.queue:
        pt1 = be.get_point_on_axis(bubble['pos'])
        pt2 = bubble['pt']
        xpts = [pt1[0], pt2[0]]
        ypts = [pt1[1], pt2[1]]
        plt.plot(xpts, ypts)
        l.append(pt2[0])
        l.append(pt2[1])

    l.append(pt[0])
    l.append(pt[1])

    b.plot_bezier_and_points(plt, l)
    # this sucks. See: http://docs.scipy.org/doc/numpy/reference/generated/numpy.polyfit.html

    plt.xlim(-50, 250)
    plt.ylim(-50, 250)
    plt.show()

