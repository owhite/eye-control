# adapted from:
#  http://stackoverflow.com/questions/12643079/bezier-curve-fitting-with-scipy/14125828

import numpy as np
from scipy.misc import comb

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
    def __init__(self, angle=None, offsetx=None, offsety=None, length=None, num=None):
        super(Bezier, self).__init__()

    def check(self):
        self.ready = True
        if angle==None:
            print 'need an angle'
            self.ready = False
        if offsetx==None:
            print 'need offsetx'
            self.ready = False
        if offsety==None:
            print 'need offsety'
            self.ready = False
        if length==None:
            print 'need length'
            self.ready = False
        if num==None:
            print 'need num'
            self.ready = False
        
    def travel(self):
        inc = self.length / self.num
        # see http://docs.python.org/2/library/collections.html#collections.deque

if __name__ == '__main__':

    from matplotlib import pyplot as plt
    import numpy as np

    b = Bezier()

    points = [155, 4, 57, 138, 25, 81, 21, 184]

    b.plot_bezier_and_points(plt, points)

    offsetx = 10
    offsety = 10
    linelength = 200
    angle = 20

    x = [offsetx, offsetx+(linelength*np.cos(np.radians(angle)))]
    y = [offsety, offsety+(linelength*np.sin(np.radians(angle)))]
    plt.plot(x, y, '-')

    plt.xlim(0, 200)
    plt.ylim(0, 200)
    plt.show()

