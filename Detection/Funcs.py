import numpy as np
import matplotlib.pyplot as plt

"""
Find and regress planes given a 3xN matrix of real world 3d points
"""
def findPlanes(pts):
    n = 0

"""
Get the equation of a plane given a 3x3 matrix of Euclidean 3D coords that it passes through
"""
def planeFromPts(pts):
    n = np.cross(np.squeeze(np.asarray(pts[:,2]))-np.squeeze(np.asarray(pts[:,0])),\
                 np.squeeze(np.asarray(pts[:,2]))-np.squeeze(np.asarray(pts[:,1])))
    return n[0], n[1], n[2], -np.dot(n, np.asarray(pts[:,2]))

"""
~done but not tested~
Given pixel/distance coords from Kinect, figure out real world [x,y,z] coords
pts is a numpy matrix of [x,y,z] col vectors for kinect x/y pixels and z distance
"""
def rwCoordsFromKinect(pts):
    #constants in the equation
    kx = (640/2) / np.tan(np.radians(57.0/2))
    ky = (480/2) / np.tan(np.radians(43.0/2))

    newx = [0] * pts.shape[1]
    newy = [0] * pts.shape[1]
    newz = [0] * pts.shape[1]

    for i in range(pts.shape[1]): #for each column vector
        newx[i] = pts[2,i] / np.sqrt((kx/pts[0,i])**2 + 1)
        newy[i] = pts[2,i] / np.sqrt((ky/pts[1,i])**2 + 1)
        newz[i] = np.sqrt(pts[2,i]**2 - newx[i]**2)

    return np.matrix([newx, newy, newz])

"""
Magnitude of a numpy array
"""
def mag(array):
    return np.sqrt(sum([el**2 for el in array]))

"""
Return the unit vector version of this array
"""
def normalized(array):
    return array / mag(array)

"""
Get 3x3 2D homogenous perspective transform matrix given source and destination points
"""
def getPTMat(src, dst):
    a = getHGFromPts(src)
    b = getHGFromPts(dst)
    return b * a.I

"""
Part of getPTMat technique - scales homogenous coords to prepare creation of transform matrix
"""
def getHGFromPts(pts): #take 3x4 homogenous matrix of column points, return 3x3
    m1 = pts[:,:-1]
    m2 = pts[:,-1]
    coeffs = m1.I * m2
    return np.multiply(np.matrix([coeffs.A1.tolist()] * 3), m1)

"""
Convert a matrix of homogenous coords to list of tuple Euclidean coords
"""
def hgToEuc(m):
    return [(m[0,i]/m[2,i], m[1,i]/m[2,i]) for i in range(m.shape[1])]