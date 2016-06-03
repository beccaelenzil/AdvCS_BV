import cv2
import random
import numpy as np
import matplotlib.pyplot as plt
import random
from Funcs import *
from primesense import openni2
from primesense import _openni2 as c_api
from mpl_toolkits.mplot3d import axes3d, Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.ion()
plt.show()

openni2.initialize()
dev = openni2.Device.open_any()
ds = dev.create_depth_stream()
ds.start()

while(1):
    f = ds.read_frame().get_buffer_as_uint16()
    a = np.ndarray((480,640),dtype=np.uint16,buffer=f)
    ipts = []
    for y in range(180, 300, 20):
        for x in range(260, 380, 20):
            ipts.append((x, y, a[y][x]))
    m = np.matrix(ipts).T
    fpts = rwCoordsFromKinect(m)
    plt.cla()
    ax.scatter([pt[0] for pt in fpts], [pt[1] for pt in fpts], [pt[2] for pt in fpts], color='r')

    a,b,c,d = planeFromPts(np.matrix(fpts[0:3]).T)
    n = np.array([a,b,c]) #vector normal to plane

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

    #print tpts
    ax.scatter([pt[0] for pt in tpts], [pt[1] for pt in tpts], [0] * len(tpts), color='y')
    plt.draw()
    plt.pause(0.1)


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