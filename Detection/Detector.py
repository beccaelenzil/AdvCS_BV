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
import operator
import xmltodict
import os

#-------------------------
# CONSTANTS
CPXTHRESH = 12 #minimum number of 'on' pixels in a corner region for it to be counted, counteracts noise
CORNER_MIN_DISTANCE = 15 #minimum distance between corners, used to avoid duplicates
HARRIS_BLOCKSIZE = 8 #corner detector parameters - block size, Sobel derivative window size, and free parameter
HARRIS_SOBEL = 9
HARRIS_K = 0.03
CORNER_THRESH = 3 #minimum value of Harris detector output that will be considered an 'on' pixel
tnames = ['arrow', 'rhombus', 'trapezoid'] #names of learned shapes to load
#-------------------------

#see if a window position was saved from a previous run, if not use the default near the center of the screen
try:
    with open("def_window.txt", 'r') as file:
        params = file.read().split(",")
        crop = [int(p) for p in params]
except:
    crop = [100,250,250,450] #default values of x1,y1,x2,y2 of rectangle selection of image to use

#width and height of subframe
fheight = crop[2]-crop[0]
fwidth = crop[3]-crop[1]

#load training data as dictionary
shapes = {}
for fname in tnames:
    shapes[fname] = getTrainingData(fname + '.xml') #trained vertex descriptors

#initialize the Kinect interface library (OpenNI) and start streams
openni2.initialize()
dev = openni2.Device.open_any()
ds = dev.create_depth_stream()
cs = dev.create_color_stream()
ds.start()
cs.start()

#the assignment problem solver used in comparison
munk = munkres.Munkres()

while 1:

    #get the color frame
    f = cs.read_frame()
    d = f.get_buffer_as_uint8()
    img = np.frombuffer(d, dtype=np.uint8)
    img.shape = (480,640,3)
    #preprocess RGB frame
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.flip(img, 1)
    img_orig = img.copy()
    img = img[crop[0]:crop[2],crop[1]:crop[3]]

    #find corners with Harris algorithm
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.blur(gray, (3,3))
    dst = cv2.cornerHarris(gray, HARRIS_BLOCKSIZE, HARRIS_SOBEL, HARRIS_K)
    c = dst * (255.0/dst.max())
    c = cv2.medianBlur(c, 3)
    ret, c = cv2.threshold(c, CORNER_THRESH, 255, cv2.THRESH_BINARY)
    cv2.imshow("corners", c)

    corners = {} #dictionary to keep track of how well supported corners are (how many px are in region)

    #ignore outer pixel border so all referenced pixels have neighbors in all directions
    for y in xrange(1, fheight-1):
       for x in xrange(1, fwidth-1):
            if c[y][x] > 0: #if any corner is found, otherwise go to next pixel

                #perform simple rectangular blob detection to make sure this is actually a corner, not just noise
                t,b,l,r = y, y+1, x, x+1 #the top, bottom, left and right coords of the rect being scanned
                didSomething = True #know to stop when nothing happens anymore
                while didSomething: #while there are neighboring 'on' pixels
                    didSomething = False
                    if (sum(c[t,l:r+1]) > 0 if t > 0 else False): #expand in each direction if there are any pixels in it
                        t -= 1
                        didSomething = True
                    if (sum(c[b,l:r+1]) > 0 if b < fheight else False):
                        b += 1
                        didSomething = True
                    if (sum(c[t:b+1,l]) > 0 if l > 0 else False):
                        l -= 1
                        didSomething = True
                    if (sum(c[t:b+1,r]) > 0 if r < fwidth else False):
                        r += 1
                        didSomething = True

                support = sum(c[t:b,l:r].flatten())/255 #how many 'on' pixels in region
                if support < CPXTHRESH: #if not enough on pixels are contained
                    continue

                corner = ((l+r)/2, (t+b)/2) #take center of rectangle as corner coordinate
                corners[corner] = support

                 #black out used pixels to avoid duplicates
                cv2.rectangle(c, (t,l), (b,r), (0,0,0), thickness=-1)

    #check to make sure there aren't any too close to each other
    pr = sorted(corners.items(), key=operator.itemgetter(1), reverse=True) #get corners in descending order of priority
    for corner in pr:
        worse = pr[pr.index(corner)+1:] #get sublist of all corners worse than this one
        for c2 in worse:
            if np.sqrt((corner[0][0] - c2[0][0])**2 + (corner[0][1] - c2[0][1])**2) < CORNER_MIN_DISTANCE:
                pr.remove(c2)
                del corners[c2[0]]

    corners = corners.keys() #other info no longer needed

    #get depth frames as DepthFrameSample instance
    dframe = fetchDepthFrames(ds, 5)

    #get 'verts' (world coordinates) from corners
    verts = []
    for c in corners:
        dx,dy,dz = colorToDepth(ds, cs, dframe, (crop[1] + c[0], crop[0] + c[1])) #IMPORTANT - offset corner coordinates by crop bounds since depth frame is full res
        if dz == 0: #invalid point, out of range in depth map, so ignore
            continue
        verts.append(np.array(openni2.convert_depth_to_world(ds, dx, dy, dz)))

        #UI stuff
        cv2.circle(img, c, 4, (255,0,0), 2)
        #ended up being too small a region for overlaid coordinate text to be visible, so nevermind this feature
        #cv2.putText(img, str(verts[-1].astype(int)), (c[0]-10,c[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)

    #draw lines between verts
    for i in range(len(corners)):
        for j in range(i+1):
            cv2.line(img, pr[i][0], pr[j][0], (0,255,0), 1)

    if len(verts) < 3: #skip if there aren't enough points to define the plane
        continue

    svds = [None] * len(verts) #sampled vertex descriptors (angles of each radiating line relative to previous)
    norm = np.cross(verts[1]-verts[0], verts[2]-verts[0]) #arbitrary normal vector for signed angle reference
    for i in range(len(verts)): #for each vertex/origin point
        ref = verts[i-1]-verts[i] #vector from current vert to previous one, really just arbitrary reference
        absangs = [angBtwn(ref, pt-verts[i], norm) for pt in verts if not np.array_equal(verts[i], pt)] #absolute angles relative to ref
        absangs.sort() #order the angles smallest to largest, starting with 0 and going CCW
        svds[i] = np.array([(absangs[idx]-absangs[idx-1])%(np.pi*2) for idx in range(len(absangs))]) #relative to each other

        #"rotate" so that smallest value is first (not to be confused with sorting, order is same but different one first)
        #m = np.argmin(svds[i])
        #if m != 0:
        #    svds[i] = np.concatenate([svds[i][m:], svds[i][:m]], 0)

    winners = []
    for sname in shapes:
        #make sure that trained descriptor has same number of vertices as what was sampled, or there will be errors
        #sometimes a corner will glitch out because of noise, and this will handle that situation
        if len(verts) != len(shapes[sname][0]):
            continue

        #get geometric length of error between training verts and sampled ones
        #the innermost list comprehension is for lining up the relative angles when determining their similarity - it gets the error at all alignments and takes the smallest
        diffs = [[min([sqmag(rotate(a2,shift)-a1) for shift in range(len(a2))]) for a1 in svds] for a2 in shapes[sname][0]]
        combos = munk.compute(diffs)

        #if this is under a threshold, then the pattern is recognized
        error = sum([diffs[row][col] for row,col in combos])
        print sname + ": " + str(error <= shapes[sname][1]) + ", error = " + str(error)

        if error < shapes[sname][1]:
            winners.append(sname)

    #make sure that any passed
    if len(winners) > 0:
        #if more than one fell beneath the threshold, take the one with the lowest error
        best = winners[np.argmin([shapes[n][1] for n in winners])]
        cv2.putText(img_orig, best, (crop[1],crop[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)

    #substitute back into original image
    img_orig[crop[0]:crop[2],crop[1]:crop[3]] = img
    cv2.rectangle(img_orig, (crop[1],crop[0]), (crop[3],crop[2]), (0,0,255), thickness=2) #highlight region of interest
    cv2.imshow('detector', img_orig)
    code = cv2.waitKey(50) #use for delay to allow time for refresh, and see if a key was pressed to shift the frame
    if code == -1: #nothing
        pass
    elif code == 2490368: #up
        crop[0] -= 5
        crop[2] -= 5
    elif code == 2621440: #down
        crop[0] += 5
        crop[2] += 5
    elif code == 2424832: #left
        crop[1] -= 5
        crop[3] -= 5
    elif code == 2555904: #right
        crop[1] += 5
        crop[3] += 5
    elif code == ord('z'): #zoom in
        crop[0] += 2
        crop[2] -= 2
        crop[1] += 2
        crop[3] -= 2
        fheight = crop[2]-crop[0]
        fwidth = crop[3]-crop[1]
    elif code == ord('x'): #zoom out
        crop[0] -= 2
        crop[2] += 2
        crop[1] -= 2
        crop[3] += 2
        fheight = crop[2]-crop[0]
        fwidth = crop[3]-crop[1]
    elif code == ord('s'): #save current frame position as default
        with open("def_window.txt", "w") as file:
            file.write(str(crop)[1:-1]) #trim off square brackets
    elif code == ord('t'): #train a new shape with the current SVDs
        #get a number to use in the filename that hasn't been used yet
        num = 0
        while os.path.isfile("shape" + str(num) + ".xml"):
            num += 1
        saveProfile(svds, "shape" + str(num) + ".xml")
        print "Profile saved to: shape" + str(num) + ".xml"

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

"""
#Old convolution method

#convolve over the image, for each pixel take the sum of differences of components with all its neighbors and use the greatest
    diff = np.ndarray((480, 640), dtype=np.uint8)
    for y in xrange(1, fheight-1):
        for x in xrange(1, fwidth-1):
            diff[y][x] = max([sum(abs(img[pxy,pxx,:]-img[y,x,:]))/3 \
                              for (pxx,pxy) in ((x,y+1), (x+1,y+1), (x+1,y), (x+1,y-1), (x,y-1), (x-1,y-1), (x-1,y), (x-1,y+1))])
    cv2.imshow('diff', diff)
"""

"""
#for averaging canny frames
for y in xrange(fheight):
        for x in xrange(fwidth):
            gray[y][x] = np.median([cframes[idx][y][x] for idx in range(CFRAME_SAMPLES)])
"""