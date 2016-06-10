import numpy as np

"""
Structure to represent a collection of depth frames, whose points can be referenced collectively
Useful for smoothing, and ignoring out-of-range zero values
"""
class DepthFrameSample:
    def __init__(self, frames):
        self.frames = frames
    """
    Get the average value at the specified point
    """
    def getPoint(self, pt):
        a = [f[pt[1]][pt[0]] for f in self.frames if f[pt[1]][pt[0]] != 0]
        if len(a) == 0: #check to make sure that all values weren't ignored
            return 0
        return np.median(a)
    """
    Crop all frames, with rectangle's upper left and lower right points given as x1,y1,x2,y2
    """
    def crop(self, w):
        for i in range(len(self.frames)):
            self.frames[i] = self.frames[i][w[0]:w[2], w[1]:w[3]]