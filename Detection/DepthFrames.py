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
        a = [f[pt[1],pt[0]] for f in self.frames if f[pt[1],pt[0]] != 0]
        if len(a) == 0: #check to make sure that all values weren't ignored
            return 0
        return int(np.median(a))
    """
    Same, but take median of points with border a around pixel
    """
    def getPointAreaAvg(self, pt, a):
        vals = []
        for y in range(pt[1]-a, pt[1]+a+1):
            for x in range(pt[0]-a, pt[0]+a+1):
                p = self.getPoint((x,y))
                if p != 0:
                    vals.append(p)
        return int(np.median(vals)) if vals != [] else 0

    """
    Crop all frames, with rectangle's upper left and lower right points given as x1,y1,x2,y2
    """
    def crop(self, w):
        for i in range(len(self.frames)):
            self.frames[i] = self.frames[i][w[0]:w[2], w[1]:w[3]]