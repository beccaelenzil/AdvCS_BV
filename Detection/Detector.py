import cv2
import random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import Funcs

im = cv2.imread("Images\\star.png")
im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(im, 100, 200, apertureSize=3)
lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, 50, 10)
for x1,y1,x2,y2 in lines[0]:
    cv2.line(im,(x1,y1),(x2,y2),(0,255,0),2)
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.imshow('image', im)
cv2.namedWindow('edges', cv2.WINDOW_NORMAL)
cv2.imshow('edges', edges)

cv2.waitKey()