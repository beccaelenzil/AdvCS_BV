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

TNAMES = ['arrow', 'rhombus', 'trapezoid'] #names of learned shapes to load
#-------------------------

"""
Recognize a 2D shape in a user-selected region.
Shape 'profiles' can be trained and saved in XML, and all loaded to be recognized.
"""
class Detector:
    """
    Get a list of corner coordinates given an input image.
    Contains code for performing Harris corner detection, thresholding, denoising, and blob detection
    Optional showCorners parameter chooses if the processed Harris output is displayed in a window for debugging
    """
    def findCorners(self, img, showCorners=False):

        #find corners with Harris algorithm
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #Harris uses grayscale image
        gray = cv2.blur(gray, (3,3)) #eliminate some noise with a modest blur
        dst = cv2.cornerHarris(gray, HARRIS_BLOCKSIZE, HARRIS_SOBEL, HARRIS_K) #run the Harris detector with the constants at the beginning of this file
        c = dst * (255.0/dst.max()) #scale the resulting image from 0 to 255
        c = cv2.medianBlur(c, 3) #eliminate more noise in the corner image
        ret, c = cv2.threshold(c, CORNER_THRESH, 255, cv2.THRESH_BINARY) #get binary thresholded image to look for corners in

        if showCorners:
            cv2.imshow("corners", c)

        corners = {} #dictionary to keep track of how well supported corners are (how many px are in region)

        #ignore outer pixel border so all referenced pixels have neighbors in all directions
        for y in xrange(1, self.fheight-1):
            for x in xrange(1, self.fwidth-1):
                if c[y][x] > 0: #see if this is an 'on' pixel (if a corner is supposedly here), otherwise go to next pixel

                    #perform simple rectangular blob detection to make sure this is actually a corner, not just noise
                    t,b,l,r = y, y+1, x, x+1 #the top, bottom, left and right coords of the rect being scanned
                    didSomething = True #know to stop when nothing happens anymore
                    while didSomething: #while there are neighboring 'on' pixels
                        didSomething = False
                        if (sum(c[t,l:r+1]) > 0 if t > 0 else False): #expand in each direction if there are any pixels in it
                            t -= 1
                            didSomething = True
                        if (sum(c[b,l:r+1]) > 0 if b < self.fheight else False):
                            b += 1
                            didSomething = True
                        if (sum(c[t:b+1,l]) > 0 if l > 0 else False):
                            l -= 1
                            didSomething = True
                        if (sum(c[t:b+1,r]) > 0 if r < self.fwidth else False):
                            r += 1
                            didSomething = True

                    support = sum(c[t:b,l:r].flatten())/255 #how many 'on' pixels are in the current region
                    if support < CPXTHRESH: #if there aren't enough in the region for it to be counted as a corner
                        continue

                    corner = ((l+r)/2, (t+b)/2) #take center of rectangle as corner coordinate
                    corners[corner] = support #save in dictionary

                    #black out used pixels to avoid duplicates
                    cv2.rectangle(c, (t,l), (b,r), (0,0,0), thickness=-1)

        #check to make sure there aren't any too close to each other
        pr = sorted(corners.items(), key=operator.itemgetter(1), reverse=True) #get corners in descending order of priority (how much support they have/how many 'on' pixels are in their region)
        for corner in pr:
            worse = pr[pr.index(corner)+1:] #get sublist of all corners worse than this one
            for c2 in worse: #if any of these corners are too close to this one, get rid of them since they're all less important
                if np.sqrt((corner[0][0] - c2[0][0])**2 + (corner[0][1] - c2[0][1])**2) < CORNER_MIN_DISTANCE:
                    pr.remove(c2)
                    del corners[c2[0]]

        return corners.keys() #other info no longer needed

    """
    Given a list of 3D vertices, get a "descriptor" of each (the angles between the rays going from it to every other vertex)
    """
    def getVertexDescriptors(self, verts):
        vds = [None] * len(verts) #vertex descriptors (angles of each radiating line relative to previous)
        norm = np.cross(verts[1]-verts[0], verts[2]-verts[0]) #arbitrary normal vector for signed angle reference
        for i in range(len(verts)): #for each vertex/origin point
            ref = verts[i-1]-verts[i] #vector from current vert to previous one, really just arbitrary reference
            absangs = [angBtwn(ref, pt-verts[i], norm) for pt in verts if not np.array_equal(verts[i], pt)] #absolute angles relative to ref
            absangs.sort() #order the angles smallest to largest, starting with 0 and going CCW
            vds[i] = np.array([(absangs[idx]-absangs[idx-1])%(np.pi*2) for idx in range(len(absangs))]) #angles relative to each other
        return vds

    """
    Takes two vertex descriptors, and returns an error value describing their similarity.
    """
    def compareDescriptors(self, vd1, vd2):
        #make sure that trained descriptor has same number of vertices as what was sampled, or there will be errors
        #sometimes a corner will glitch out because of noise, and this will handle that situation
        if len(vd1) != len(vd2):
            return sys.maxint

        #get geometric length of error between training verts and sampled ones
        #the innermost list comprehension is for lining up the relative angles when determining their similarity - it gets the error at all alignments and takes the smallest
        diffs = [[min([sqmag(rotate(a2,shift)-a1) for shift in range(len(a2))]) for a1 in vd1] for a2 in vd2]
        #attempt to pair off the vertices from each descriptor, such that the sum of the errors of each pairing is minimized
        combos = self.munk.compute(diffs)

        #return the total error
        return sum([diffs[row][col] for row,col in combos])

    """
    Main function to control UI
    """
    def __init__(self):
        #see if a window position was saved from a previous run, if not use the default window near the center of the screen
        try:
            with open("def_window.txt", 'r') as file:
                params = file.read().split(",")
                self.crop = [int(p) for p in params]
        except:
            self.crop = [100,250,250,450] #default values of x1,y1,x2,y2 of rectangle selection of image to use

        #width and height of subframe
        self.fheight = self.crop[2]-self.crop[0]
        self.fwidth = self.crop[3]-self.crop[1]

        #load training data (shape profiles) as dictionary
        shapes = {}
        for fname in TNAMES:
            shapes[fname] = getTrainingData(fname + '.xml') #trained vertex descriptors

        #initialize the Kinect interface library (OpenNI) and start streams
        openni2.initialize()
        dev = openni2.Device.open_any()
        ds = dev.create_depth_stream()
        cs = dev.create_color_stream()
        ds.start()
        cs.start()

        #the assignment problem solver used in comparison
        self.munk = munkres.Munkres()

        while 1: #loop indefinately

            #get the color frame from the Kinect
            f = cs.read_frame()
            d = f.get_buffer_as_uint8()
            img = np.frombuffer(d, dtype=np.uint8)
            img.shape = (480,640,3)

            #preprocess the RGB frame
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) #order of color components swapped
            img = cv2.flip(img, 1) #some reason it's mirrored horizontally... this fixes it
            img_orig = img.copy() #this original copy is used later when displaying the final output
            img = img[self.crop[0]:self.crop[2],self.crop[1]:self.crop[3]] #trim down to the user selected region of interest

            #get depth frames as DepthFrameSample instance
            #this function gets a median average of numerous depth frames, helps avoid noise
            dframe = fetchDepthFrames(ds, 3)

            #Get a list of corners in the region of interest
            corners = self.findCorners(img, showCorners=True)

            #get 'verts' (world coordinates) from corners
            verts = []
            for c in corners:
                #get depth coodinate equivolents of each corner
                dx,dy,dz = colorToDepth(ds, cs, dframe, (self.crop[1] + c[0], self.crop[0] + c[1])) #IMPORTANT - offset corner coordinates by crop bounds since depth frame is full res

                #check if this is an invalid point (if it's out of range in the depth map)
                if dz == 0:
                    continue

                #then get world coordinates and save to array
                verts.append(np.array(openni2.convert_depth_to_world(ds, dx, dy, dz)))

                #Circle the found corners on the final image
                cv2.circle(img, c, 4, (255,0,0), 2)

            #skip this round if there aren't enough points to define a plane... one must have gotten lost
            if len(verts) < 3:
                continue

            #get the descriptors of the sampled vertices
            svds = self.getVertexDescriptors(verts)

            winners = []
            for sname in shapes:
                error = self.compareDescriptors(svds, shapes[sname][0]) #compare each shape profile to the detected descriptor

                #if the error is under the threshold given by the shape profile, then the shape is recognized
                if error < shapes[sname][1]:
                    winners.append(sname)
                print sname + ": " + str(error <= shapes[sname][1]) + ", error = " + str(error)

            #make sure that any were accepted
            if len(winners) > 0:
                #if more than one fell beneath the threshold, take the best one (the one with the lowest error)
                best = winners[np.argmin([shapes[n][1] for n in winners])]
                #label the winner
                cv2.putText(img_orig, best, (self.crop[1],self.crop[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)

            #substitute the region of interest back into original image
            img_orig[self.crop[0]:self.crop[2],self.crop[1]:self.crop[3]] = img
            cv2.rectangle(img_orig, (self.crop[1],self.crop[0]), (self.crop[3],self.crop[2]), (0,0,255), thickness=2) #highlight region of interest
            cv2.imshow('detector', img_orig) #update in window

            #use for delay to allow time for refresh, and see if a key was pressed to shift/scale the frame location
            code = cv2.waitKey(50)
            if code == -1: #nothing
                pass
            elif code == 2490368: #up
                self.crop[0] -= 5
                self.crop[2] -= 5
            elif code == 2621440: #down
                self.crop[0] += 5
                self.crop[2] += 5
            elif code == 2424832: #left
                self.crop[1] -= 5
                self.crop[3] -= 5
            elif code == 2555904: #right
                self.crop[1] += 5
                self.crop[3] += 5
            elif code == ord('z'): #zoom in
                self.crop[0] += 2
                self.crop[2] -= 2
                self.crop[1] += 2
                self.crop[3] -= 2
                self.fheight = self.crop[2]-self.crop[0]
                self.fwidth = self.crop[3]-self.crop[1]
            elif code == ord('x'): #zoom out
                self.crop[0] -= 2
                self.crop[2] += 2
                self.crop[1] -= 2
                self.crop[3] += 2
                self.fheight = self.crop[2]-self.crop[0]
                self.fwidth = self.crop[3]-self.crop[1]
            #save current frame position as default - mostly useful in debugging, since you don't have to readjust frame location every time the program starts
            elif code == ord('s'):
                with open("def_window.txt", "w") as file:
                    file.write(str(self.crop)[1:-1]) #trim off square brackets and write to file
            #train a new shape with the current sampled vertex descriptors
            elif code == ord('t'):
                #get a number to use in the filename that hasn't been used yet
                num = 0
                while os.path.isfile("shape" + str(num) + ".xml"):
                    num += 1
                saveProfile(svds, "shape" + str(num) + ".xml") #handles the XML encoding
                print "Profile saved to: shape" + str(num) + ".xml"

#main call
Detector()