import cv2
import numpy as np



cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.imshow('image', im)
cv2.namedWindow('edges', cv2.WINDOW_NORMAL)
cv2.imshow('edges', edges)
cv2.waitKey()