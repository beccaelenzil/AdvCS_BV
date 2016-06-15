from Funcs import *
import random
import numpy as np

"""
---OBSOLETE---

Modified perceptron for regressing a plane given 3D points.
Unlike a normal perceptron, it tries to make w.x = 0 for all x's given, instead of just above/below the threshold
Ended up not working that well
"""
class Perceptron:
    def __init__(self):
        self.w = None
    def train(self, data, rate, iters):
        pts = np.asarray(data.T) #make into array
        self.w = np.array([0.1] * (data.shape[0]+1))
        for i in range(iters): #use gradient descent method to adjust the weights a constant fraction of the dot product of the weights and a training point
            pt = random.choice(pts)
            e = np.dot(self.w, np.append(pt, np.array([1])))
            self.w += rate * -e * normalized(np.append(pt, np.array([1])))

    def trainDynamicRate(self, data, ri, rk, iters): #same but learning rate decreases as function of iteration number
        pts = np.asarray(data.T) #make into array
        self.w = np.array([0.1] * data.shape[0])
        for i in range(iters):
            pt = random.choice(pts)
            e = np.dot(self.w, pt)
            self.w += ri*np.e**(-rk*i) * -e * normalized(pt)

    def avgerror(self, set): #if 3XN matrix of pts has a average error < thresh
        e = 0
        for i in range(set.shape[1]):
            e += abs(np.dot(self.w, np.asarray(set[:,i]).flatten())) #dot product is ideally 0, so take absolute value as error
        e /= set.shape[1] #average
        return e
    def __repr__(self):
        return "Perceptron with weights " + str(self.w)