import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def mag(array):
    return np.sqrt(sum([el**2 for el in array]))

def normalized(array):
    return array / mag(array)

def getPTMat(src, dst):
    a = getHGFromPts(src)
    b = getHGFromPts(dst)
    return b * a.I

def getHGFromPts(pts): #take 3x4 homogenous matrix of column points, return 3x3
    m1 = pts[:,:-1]
    m2 = pts[:,-1]
    coeffs = m1.I * m2
    return np.multiply(np.matrix([coeffs.A1.tolist()] * 3), m1)

def hgToEuc(m): #matrix of homogenous coords to list of tuple Euclidean coords
    return [(m[0,i]/m[2,i], m[1,i]/m[2,i]) for i in range(m.shape[1])]

def planeFromPts(pts): #3x3 Euclidean 3d coords to find plane eq through
    n = np.cross(np.squeeze(np.asarray(pts[:,2]))-np.squeeze(np.asarray(pts[:,0])),\
                 np.squeeze(np.asarray(pts[:,2]))-np.squeeze(np.asarray(pts[:,1])))
    return n[0], n[1], n[2], -np.dot(n, np.asarray(pts[:,2]))

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

unitSquareOnPlaneDemo()