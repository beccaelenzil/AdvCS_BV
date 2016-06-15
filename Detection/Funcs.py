import numpy as np
import numpy.linalg as linalg
from primesense import openni2
from matplotlib import pyplot as plt
import sys
from DepthFrames import DepthFrameSample
import xmltodict

#---------------------------------------------
# All the utility math/image processing functions that are needed in the main one
# Lots are unused since they were implemented for old approaches
#---------------------------------------------

"""
Averages n depth frames, returns world coodinates of 2d depth pixel coordinates given in pts array
Also takes depth stream (ds) instance for reference
"""
def fetchDepthFrames(ds, n):
    #fetch n sequential frames
    frames = [None] * n
    for i in range(n): #get n frames
        f = ds.read_frame().get_buffer_as_uint16()
        frames[i] = np.ndarray((480,640),dtype=np.uint16,buffer=f)
        plt.pause(1.0/30) #assume 30 fps
    return DepthFrameSample(frames)

"""
weird inefficient but necessary method to get depth point from color
ds - depth stream
cs - color stream
dframe - depth frame (as DepthFrameSample)
pt - color point to convert
"""
def colorToDepth(ds, cs, dframe, pt):
    guess = [pt[0], pt[1]] #guess for which depth point it is, start by assuming they're same point
    bestErr = sys.maxint
    bestGuess = None
    while True:
        cpt = openni2.convert_depth_to_color(ds, cs, guess[0], guess[1], dframe.getPointAreaAvg(guess, 1)) #calculate color point with current guess

        #check if its right or hit local minimum (then just give up and give best one)
        if cpt == pt or ((cpt[0] - pt[0])**2 + (cpt[1] - pt[1])**2) > bestErr:
            return (bestGuess[0], bestGuess[1], dframe.getPointAreaAvg(bestGuess, 1))
        bestErr = (cpt[0] - pt[0])**2 + (cpt[1] - pt[1])**2 #update best error
        bestGuess = guess

        if cpt[0] < pt[0]: #adjust guess based on result
            guess[0] += 1
        elif cpt[0] > pt[0]:
            guess[0] -= 1
        if cpt[1] < pt[1]:
            guess[1] += 1
        elif cpt[1] > pt[1]:
            guess[1] -= 1

"""
Get the equation of a plane given a 3x3 matrix of Euclidean 3D coords that it passes through
"""
def planeFromPts(pts):
    n = np.cross(np.squeeze(np.asarray(pts[:,2]))-np.squeeze(np.asarray(pts[:,0])),\
                 np.squeeze(np.asarray(pts[:,2]))-np.squeeze(np.asarray(pts[:,1]))) #get normal vector to use as (a,b,c) values
    return (n[0], n[1], n[2], -np.dot(n, np.asarray(pts[:,2]))[0]) #get d offset with dot product

"""
Fit a plane to the given list of points
Another old approach that never worked very well
"""
def fitPlane(pts):
    xs = np.array([pt[0] for pt in pts])
    ys = np.array([pt[1] for pt in pts])
    zs = np.array([pt[2] for pt in pts])
    sxx = sum(xs**2)
    sxy = sum(xs*ys)
    syy = sum(ys**2)
    sx = sum(xs)
    sy = sum(ys)
    a = np.matrix([[sxx, sxy, sx],\
                   [sxy, syy, sy],\
                   [sx,  sy,  len(pts)]])
    b = np.matrix([[sum(xs*zs)], [sum(ys*zs)], [sum(zs)]])
    x = np.asarray(a.I * b).flatten()
    return (x[0], x[1], x[2], np.mean([-np.dot(pt, x) for pt in pts]))

"""
Given pixel/distance coords from Kinect, figure out real world [x,y,z] coords
pts is a numpy matrix of [x,y,z] col vectors for kinect x/y pixels and z distance
I realized that there's a more accurate built-in function to do this after I had already finished this code, but here it is anyway
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
Square magnitude of a numpy array
"""
def sqmag(array):
    return sum([el**2 for el in array])

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

"""
Skew-symmetric cross product
"""
def sscp(v):
    return np.matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])

"""
Gets counterclockwise angle between vectors (needs plane normal for signed angle)
"""
def angBtwn(v1, v2, n):
    c = np.dot(v1, v2)/(mag(v1)*mag(v2)) #sine and cosine of angle
    c = max(min(c, 1), -1) #make sure it doesn't go out of range and cause NaN (sometimes small rounding errors cause this)
    a = np.arccos(c)
    if np.dot(np.cross(v1,v2), n) < 0: #check direction with normal vector, switch sign if its backwards
        a = 2*np.pi - a
    return a

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

"""
"rotates" a 1D array to put the element at idx=shift first
Doesn't change order
"""
def rotate(array, shift):
    return np.concatenate([array[shift:], array[:shift]], 0)

"""
Loads a shape "profile" from a XML file.
Returns a 2D array of vertex descriptors like the one found in, and the recommended threshold for the shape to be recognized
Will throw exception if file not found
"""
def getTrainingData(name):
    tvds = []
    with open(name) as f:
        doc = xmltodict.parse(f.read())
        thresh = float(doc["shape"]["@thresh"])
        for vert in doc["shape"]["vert"]:
            angs = []
            for ang in vert["angle"]:
                angs.append(float(ang))
            tvds.append(np.array(angs))
    return tvds, thresh

"""
Writes a shape profile to an XML file, given a 2D array of vertex descriptors
"""
def saveProfile(vds, fname):
    with open(fname, "w") as f:
        f.write("<shape thresh=\"1\">\n") #no way of knowing threshold, just default to 1
        for vert in vds:
            f.write("    <vert>\n")
            for angle in vert:
                f.write("        <angle>" + str(angle) + "</angle>\n")
            f.write("    </vert>\n")
        f.write("</shape>")