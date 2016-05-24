import matplotlib.pyplot as plt
import numpy as np

def getHGFromPts(pts): #take 3x4 homogenous matrix of column points, return 3x3
    m1 = pts[:,:-1]
    m2 = pts[:,-1]
    coeffs = m1.I * m2
    return np.multiply(np.matrix([coeffs.A1.tolist()] * 3), m1)

b1x = [0, 1, 1, 0]
b1y = [1, 1, 0, 0]

b2x = [.45, .55, .3, .8]
b2y = [.8, .8, .4, .4]

print getHGFromPts(np.matrix([b1x, b1y, [1]*4]))
