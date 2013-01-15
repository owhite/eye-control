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


if __name__ == '__main__':
    from matplotlib import pyplot as plt

    points = [155.95185909, 4.64042794, 57.74101074, 138.1875438, 25.93409495, 81.44692581,21.16373321, 184.4609643]

    b = Bezier()

    bezier = b.bezier_curve(points, nTimes=1000)

    # split_pairs is a utility to convert to plt.plot's funky format
    xpoints, ypoints = b.split_pairs(points) 
    xvals, yvals = b.split_pairs(bezier)

    plt.plot(xvals, yvals)

    plt.plot(xpoints, ypoints, "ro")
    for nr in range(len(xpoints)):
        plt.text(xpoints[nr], ypoints[nr], nr)

    plt.show()

