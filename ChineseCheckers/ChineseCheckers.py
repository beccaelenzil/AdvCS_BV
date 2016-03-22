from visual import *
import math

"""
coordinate system:
origin at bottom circle
(units moving diagonal northwest (f), units moving diagonal northeast (g))
"""
class Marble:
    def __init__(self, f, g, player):
        self.f = f
        self.g = g
        self.player = player
        self.colors = [color.red, color.orange, color.yellow, color.green, color.blue, color.white]
        self.sphere = sphere(pos = ((g-f)/2.0, (g+f)*math.sqrt(3)/2, 0), radius=0.3, color = self.colors[player])
    def update(self):
        self.sphere.pos = pos = ((self.g-self.f)/2.0, (self.g+self.f)*math.sqrt(3)/2, 0)
    def __repr__(self):
        return "Player " + str(self.player) + "'s marble at (" + str(self.f) + ", " + str(self.g) + ")"
    def __iadd__(self, coord):
        self.f += coord[0]
        self.g += coord[1]
        self.update()

class Board:
    def __init__(self, players):
        self.players = players
        self.board = cylinder(pos = (0, 7, -.5), axis = (0, 0, .5), radius = 8, height = .5, material = materials.wood)
        self.marbles = []
        startPts = [(0, 0), (8, -1), (9, 0), (8, 8), (0, 9), (-1, 8)]
        for p in range(6):
            for f in range(4):
                for g in range(4 - f):
                    self.marbles.append(Marble(startPts[p][0] + f * (-1 if p%2==1 else 1), startPts[p][1] + g * (-1 if p%2==1 else 1), p))
    def hostGame(self):
        while(true):
            print "waiting"
            scene.kb.getkey()
            print "got it"
            self.marbles[9] += (1, 0)

b = Board(6)
b.hostGame()