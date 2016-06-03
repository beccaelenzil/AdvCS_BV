import numpy as np
import numpy.linalg as linalg
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
    return (n[0], n[1], n[2], -np.dot(n, np.asarray(pts[:,2]))[0])

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

    return [(newx[i], newy[i], newz[i]) for i in range(len(newx))]

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

def hgToEuc3D(m):
    return [(m[0,i]/m[3,i], m[1,i]/m[3,i], m[2,i]/m[3,i]) for i in range(m.shape[1])]

def hgToEuc3DArray(m):
    return [(el[0]/el[3], el[1]/el[3], el[2]/el[3]) for el in m]

"""
Skew-symmetric cross product
"""
def sscp(v):
    return np.matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])

"""
Gets angle between vectors
"""
def angBtwn(v1, v2):
    return np.arccos(np.dot(v1, v2)/(mag(v1)*mag(v2)))

"""
Gives the transform between A and B, two Nx3 matrices of column vectors.
Transform represented as p' = Rp + t
Returns R,t
Uses nasty linear algebra stuff, so approach is HEAVILY based on: http://nghiaho.com/uploads/code/rigid_transform_3D.py_
"""
def rigid_transform(A, B):
    if len(A) != len(B):
        print "Matrix dimension mismatch in rigid transform"
        return None
    n = A.shape[0]

    #get centroids
    ctrA = np.mean(A, axis=0)
    ctrB = np.mean(B, axis=0)

    #adjust shapes to have same center
    AA = A - np.tile(ctrA, (n, 1))
    BB = B - np.tile(ctrB, (n, 1))

    #gross...
    H = AA.T * BB
    U, S, Vt = linalg.svd(H)
    R = Vt.T * U.T
    if linalg.det(R) < 0:
        Vt[2,:] *= -1
        R = Vt.T * U.T
    t = -R*ctrA.T + ctrB.T

    return R, t