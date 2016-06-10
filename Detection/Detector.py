import cv2
import random
import numpy as np
import matplotlib.pyplot as plt
import random
from Funcs import *
from primesense import openni2
from primesense import _openni2 as c_api
from mpl_toolkits.mplot3d import axes3d, Axes3D
import ctypes
import munkres
import time

def getTrainingData():
    return np.array([[]])

crop = (170,250,300,450) #x1,y1,x2,y2 of rectangle selection of image to use
fheight = crop[2]-crop[0]
fwidth = crop[3]-crop[1]

openni2.initialize()
dev = openni2.Device.open_any()
ds = dev.create_depth_stream()
cs = dev.create_color_stream()
ds.start()
cs.start()

munk = munkres.Munkres()

while(1):
    #get the color frame
    f = cs.read_frame()
    d = f.get_buffer_as_uint8()
    img = np.frombuffer(d, dtype=np.uint8)
    img.shape = (480,640,3)
    #preprocess RGB frame
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.flip(img, 1)
    img = img[crop[0]:crop[2],crop[1]:crop[3]]

    frames = fetchDepthFrames(ds, 4) #get frames as DepthFrameSample instance
    frames.crop(crop)

    #find corners with Harris algorithm
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    #gray = cv2.Canny(gray, 10, 50, apertureSize=3)
    cv2.imshow('gray', gray)
    dst = cv2.cornerHarris(gray, 12, 5, 0.04)
    thresh = dst.max() * 0.01
    corners = []

    ucorners = [] #unfiltered corners
    for y in xrange(fheight):
        for x in xrange(fwidth):
            if dst[y][x] > thresh:
                ucorners.append([x, y])

    usedcorners = []
    for c in ucorners:
        if c in usedcorners:
            continue
        d = [(uc[0]-c[0], uc[1]-c[1]) for uc in ucorners] #distances from current corner to all others
        closecorners = []
        for i in range(len(d)):
            if mag(d[i]) < 50: #if close
                closecorners.append(ucorners[i])
                usedcorners.append(ucorners[i])
        if len(closecorners) == 0:
            continue
        corners.append((int(np.median([el[0] for el in closecorners])), int(np.median([el[1] for el in closecorners])))) #use centroid

    for c in corners:
        #get equivalent depth point and add to list
        #dpt = colorToDepth(ds, cs, frames, (x,y))

        #draw onto UI to show found corners, and label coordinates
        cv2.circle(img, c, 4, (255,0,0), 2)
        #cv2.putText(img, str(openni2.convert_depth_to_world(ds, dpt[0], dpt[1], frames.getPoint(dpt))),\
        #            (x+8,y+8), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,255,0), 2, cv2.LINE_AA)

    fpts = processDepthFrames(ds, frames, corners) #average frames and get the needed points
    pts = np.array(fpts) #list of world coords of corners

    #draw lines between verts
    for i in range(len(corners)):
        for j in range(i+1):
            cv2.line(img, corners[i], corners[j], (0,255,0), 1)

    """
    #get origin (centroid)
    o = np.array([np.mean([el[0] for el in pts]), np.mean([el[1] for el in pts]), np.mean([el[1] for el in pts])])
    vs = pts - o #relative vectors

    svds = np.array([[]] * len(pts)) #sampled vertex descriptors (angles of each radiating line relative to previous)
    norm = np.cross(pts[0], pts[1]) #arbitrary normal vector for signed angle reference
    for i in range(len(pts)): #for each vertex/origin point
        absangs = np.array([angBtwn(pts[0]-pts[i], pt-pts[i], norm) for pt in pts if pts[i] != pt]) #absolute angles relative to pts[0]-pts[i] (vector from current vert to first corner)
        absangs.sort() #order the angles, starting with 0 and going CCW
        svds[i] = [(absangs[idx]-absangs[idx-1])%(np.pi*2) for idx in range(len(absangs))] #relative to each other
        svds[i] = svds[i][np.argmin(svds[i]):] + svds[i][:np.argmin(svds[i])] #"rotate" so that smallest value is first (not to be confused with sorting, order is same but different one first)

    #STILL NEED TO IMPLEMENT
    tverts = getTrainingData() #trained vertices
    #-------------------------------------------

    diffs = [[sqmag(a2-a1) for a1 in svds] for a2 in tverts] #get geometric length of error between training verts and sampled ones
    combos = munk.compute(diffs)

    #if this is under a threshold, then the pattern is recognized
    error = sum([diffs[row][col] for row,col in combos])
    print error
    """

    cv2.imshow('detector', img)
    cv2.waitKey(50) #use for delay to allow time for refresh - can't find designated wait function??? But this works

#OLD CRAP
#im = cv2.imread("Images\\star.png")
#im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
#edges = cv2.Canny(im, 100, 200, apertureSize=3)
#lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, 50, 10)
#for x1,y1,x2,y2 in lines[0]:
#    cv2.line(im,(x1,y1),(x2,y2),(0,255,0),2)
#cv2.namedWindow('image', cv2.WINDOW_NORMAL)
#cv2.imshow('image', im)
#cv2.namedWindow('edges', cv2.WINDOW_NORMAL)
#cv2.imshow('edges', edges)

#cv2.waitKey()

"""
---More old stuff---
p1 = np.array([0, 0, -d/c]) #point on plane at x = 0, y = 0
p2 = np.array([1, 0, -(a+d)/c]) #point at  x = 1, y = 0
#vertices
v = [None] * 3
v[0] = normalized(p2-p1) * np.sqrt(2)/2 #get vector in plane with mag root2/2 to make unit square
v[2] = -v[0] #same in opposite direction
v[1] = normalized(np.cross((a,b,c), v[0])) * np.sqrt(2)/2 #perpendicular to normal and first line
v = [el + p1 for el in v] #adjust height to make coplanar

#source 4x4 matrix with source normal and 3 homogenous points
ms = np.matrix([[ps[0], ps[1], ps[2], 0], v[0].tolist() + [1], v[1].tolist() + [1], v[2].tolist() + [1]]).T
#destination 4x4 matrix
md = np.matrix([[0, 0, 1, 0], [-.5, -.5, 0, 1], [.5, -.5, 0, 1], [.5, .5, 0, 1]]).T
t = md * ms.I

#transform all the points then de-homogenize them
tptshg = t * np.matrix(np.matrix(fpts).T.tolist() + [[1]*len(fpts)])
tpts = [(pt[0]/pt[3], pt[1]/pt[3], pt[2]/pt[3]) for pt in tptshg.T.tolist()]

ax.scatter([pt[0] for pt in tpts], [pt[1] for pt in tpts], [pt[2] for pt in tpts], color='y')
"""

"""
a = normalized(np.array(fpts[1])-np.array(fpts[0]))
    b = np.array([0, 1, 0])
    v = np.cross(a, b)
    s = mag(v)
    c = np.dot(a, b)
    r = np.identity(3) + sscp(v) + sscp(v)**2 * (1-c)/(s**2)

    tpts = [None] * len(fpts)
    for i in range(len(fpts)):
        p = np.array(fpts[i])
        tpts[i] = (r * np.matrix(normalized(p)).T) * mag(p)
"""

"""
o = np.array([0, 0, -d/c]) #the effective origin (the point on the plane with x=y=0
    v1 = np.array(fpts[0] - o) #the vector from origin to the first point on the plane
    v2 = np.array([v1[0], v1[2], 0]) #vector parallel to XY plane
    theta = np.arccos(np.dot(v1, v2) / (mag(v1)*mag(v2))) #angle between them
    axis = np.cross(v1, v2) #axis perpendicular to these vectors to rotate around

    tpts = [None] * len(fpts)
    a,b,c = o
    u,v,w = axis
    for i in range(len(fpts)):
        x,y,z = fpts[i]
        tpts[i] = np.array([\
            (a*(v**2+w**2)-u*(b*v+c*w-u*x-v*y-w*z))*(1-np.cos(theta)) + (u**2+v**2+w**2)*x*np.cos(theta) + np.sqrt(u**2+v**2+w**2)*(-c*v+b*w-w*y+v*z)*np.sin(theta),\
            (b*(v**2+w**2)-v*(a*u+c*w-u*x-v*y-w*z))*(1-np.cos(theta)) + (u**2+v**2+w**2)*y*np.cos(theta) + np.sqrt(u**2+v**2+w**2)*(c*u-a*w+w*x-u*z)*np.sin(theta),\
            (c*(u**2+v**2)-w*(a*u+b*v-u*x-v*y-w*z))*(1-np.cos(theta)) + (u**2+v**2+w**2)*z*np.cos(theta) + np.sqrt(u**2+v**2+w**2)*(-b*u+a*v-v*x+u*y)*np.sin(theta)])\
            /(u**2+v**2+w**2)
"""

"""
plane_vector = np.cross(np.array([0,1,0]), n) #a random vector in the plane
    o = np.array([0, 0, -d/c]) #the origin at x=y=0
    v = [None] * 4 #vertices of a unit square on the plane
    v[0] = normalized(plane_vector) * np.sqrt(2)/2
    v[1] = normalized(np.cross(n, v[0]))
    v[2] = -v[0]
    v[3] = -v[1]
    v = [el + o for el in v] #adjust to put on origin

    verts2d = [None] * 4
    for i in range(4): #convert world to color
        verts2d[i] = openni2.convert_world_to_depth(ds, v[i][0], v[i][1], v[i][2])
        verts2d[i] = openni2.convert_depth_to_color(ds, cs,\
                                                    int(verts2d[i][0]),\
                                                    int(verts2d[i][1]),\
                                                    int(verts2d[i][2]))
"""

"""
 #move all points onto the plane
    ppts = [None] * len(fpts)
    for i in range(len(fpts)):
        pt = np.array(fpts[i])
        #get point of intersection of plane with normal line going through
        s = -(a*pt[0] + b*pt[1] + c*pt[2] + d)/np.dot(n, n)
        ppts[i] = pt + s*n

    #now get polar coordinates
    pcoords = [None] * len(fpts)
    o = ppts[0] #define an origin
    v1 = normalized(ppts[1]-o) #a vector parallel to the plane to get angles against
    for i in range(len(ppts)):
        pcoords[i] = (mag(ppts[i]-o), angBtwn(v1, ppts[i]-o))

    tpts = [(r*np.cos(theta), r*np.sin(theta)) for (r,theta) in pcoords]
"""