import random
from Funcs import *
from Perceptron import Perceptron
from primesense import openni2
import numpy as np
import matplotlib.pyplot as plt
import time
import cv2

def planeFromPtsDemo():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    xs = [1, 2, 4]
    ys = [5, 9, 3]
    zs = [8, 6, 5]
    m = np.matrix([xs, ys, zs])
    ax.scatter(xs, ys, zs, c='r')

    p = planeFromPts(m)
    newxs = [random.random()*10 for i in range(50)]
    newys = [random.random()*10 for i in range(50)]
    a, b, c, d = p
    newzs = [(a*newxs[i] + b*newys[i] + d)/(-c) for i in range(50)]
    ax.scatter(newxs, newys, newzs, c='b')

    plt.show()

def unitSquareOnPlaneDemo():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    xs = [1, 2, 4]
    ys = [5, 9, 3]
    zs = [8, 6, 5]
    m = np.matrix([xs, ys, zs])
    a, b, c, d = planeFromPts(m)

    p1 = np.array([0, 0, -d/c]) #point on plane at x = 0, y = 0
    p2 = np.array([1, 0, -(a+d)/c]) #point at  x = 1, y = 0
    v = [None] * 4
    v[0] = normalized(p2-p1) * np.sqrt(2)/2 #get vector in plane with mag root2/2 to make unit square
    v[2] = -v[0] #same in opposite direction
    v[1] = normalized(np.cross((a,b,c), v[0])) * np.sqrt(2)/2 #perpendicular to normal and first line
    v[3] = -v[1]

    v = [el + p1 for el in v] #adjust height to make coplanar

    ax.scatter(xs, ys, zs, c='r')
    ax.scatter([el[0] for el in v], [el[1] for el in v], [el[2] for el in v], c='g')
    ax.scatter([0], [0], [-d/c], c='b')
    plt.show()

def perceptronDemo():
    m = np.matrix([[1,2],[2,4],[3,6]]).T
    p = Perceptron()
    p.trainDynamicRate(m, .2, 0.01, 100)
    print p
    print "Total error: "
    print p.avgerror(m)

def perspectiveTransformDemo():
    b1x = [0, 1, 1, 0]
    b1y = [1, 1, 0, 0]

    b2x = [.45, .55, .3, .8]
    b2y = [.8,  .8,  .4, .4]

    src = np.matrix([b1x, b1y, [1]*4])
    dst = np.matrix([b2x, b2y, [1]*4])
    t = getPTMat(src, dst)

    #test transform matrix by turning dest points back into source
    orig = hgToEuc(t.I * dst) #array of tuple points
    plt.scatter([orig[i][0] for i in range(len(orig))], [orig[i][1] for i in range(len(orig))], color='red')
    plt.scatter(b2x, b2y, color='blue') #dest points
    plt.show()

im = None
def kinectDemo():
    fig = plt.figure()
    openni2.initialize()
    dev = openni2.Device.open_any()
    ds = dev.create_depth_stream()
    ds.start()
    f = ds.read_frame().get_buffer_as_uint16()
    a = np.ndarray((480,640),dtype=np.uint16,buffer=f)
    im = plt.imshow(a)
    plt.show()

kinectDemo()