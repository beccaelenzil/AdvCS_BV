from visual import *
import math

"""
coordinate system:
origin at bottom circle
(units moving diagonal northwest (f), units moving diagonal northeast (g))
"""
class Marble:
    def __init__(self, f, g, player):
        """
        Add a doc string describing what f and g are at minimum
        """
        self.f = f
        self.g = g
        self.player = player
        self.colors = [color.red, color.orange, color.yellow, color.green, color.blue, color.white]
        self.sphere = sphere(pos = ((g-f)/2.0, (g+f)*math.sqrt(3)/2, 0), radius=0.3, color = self.colors[player])
    def update(self):
        self.sphere.pos = ((self.g-self.f)/2.0, (self.g+self.f)*math.sqrt(3)/2, 0)
    def __repr__(self):
        return "Player " + str(self.player) + "'s marble at (" + str(self.f) + ", " + str(self.g) + ")"
    def __iadd__(self, coord):
        self.f += coord[0]
        self.g += coord[1]
        self.update()

class Hole:
    def __init__(self, f, g, marble):
        """
        Add a doc string describing what f and g are at minimum
        """
        self.f = f
        self.g = g
        self.marble = marble
        self.shape = cylinder(pos = ((self.g-self.f)/2.0, (self.g+self.f)*math.sqrt(3)/2, -.295), axis = (0, 0, .3), radius = 0.3, height = .3, color = color.black)
    def highlight(self, hl):
        if hl:
            self.shape.color = color.yellow
        else:
            self.shape.color = color.black
    def __repr__(self):
        return "(" + str(self.f) + ", " + str(self.g) + "), " + ("occupied by a " + str(self.marble.sphere.color) + " marble" if self.marble != None else " empty")

class Board:
    def __init__(self, players):
        self.players = players
        self.board = cylinder(pos = (0, 7, -.5), axis = (0, 0, .5), radius = 8, height = .5, material = materials.wood)
        self.marbles = [[None] * 12] * 12
        startPts = [(0, 0), (8, -1), (9, 0), (8, 8), (0, 9), (-1, 8)]
        self.holes = [[None] * 12] * 12
        for p in range(6):
            for f in range(4):
                for g in range(4 - f):
                    self.marbles[f][g] = Marble(startPts[p][0] + f * (-1 if p%2==1 else 1), startPts[p][1] + g * (-1 if p%2==1 else 1), p)
                    self.holes[f][g] = Hole(f, g, self.marbles[f][g])
        self.unitmoves = [(0, 1), (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1)]
        #make holes
        for startf in range(4):
            loc = (startf, 4)
            for move in self.unitmoves:
                for n in range(4 - startf):
                    self.holes[loc[0]][loc[1]] = Hole(loc[0], loc[1], None)
                    loc = (loc[0] + move[0], loc[1] + move[1])
        self.holes[4][4] = Hole(4, 4, None)

    def hostGame(self):
        prevSelectedShape = None
        prevSelectedColor = None
        turn = 0
        while(True):
            while not scene.mouse.clicked:
                p = scene.mouse.pick
                if prevSelectedShape != p:
                    if prevSelectedShape != None:
                            prevSelectedShape.color = prevSelectedColor
                    if p != None and len([x for x in range(len(self.marbles) * len(self.marbles[0]))\
                                          if self.marbles[x/len(self.marbles)][x%len(self.marbles)] != None and self.marbles[x/len(self.marbles)][x%len(self.marbles)].sphere == p]) > 0:
                        prevSelectedColor = p.color
                        p.color = color.magenta
                        prevSelectedShape = p
                sleep(0.1)
            obj = scene.mouse.pick
            scene.mouse.getclick()
            themarbles = [self.marbles[x/len(self.marbles)][x%len(self.marbles)] for x in range(len(self.marbles) * len(self.marbles[0]))\
                                          if self.marbles[x/len(self.marbles)][x%len(self.marbles)] != None and self.marbles[x/len(self.marbles)][x%len(self.marbles)].sphere == obj]
            if len(themarbles)==0:
                continue
            marble = themarbles[0]
            #see if are within 1 unit in both directions, and also check to see if diff is not same for both b/c (-1,-1), (0,0), and (1, 1) aren't legal
            selectables = []
            for x in range(len(self.holes)):
                if abs(self.holes[x].f-marble.f) <= 1 and abs(self.holes[x].g-marble.g) <= 1 and (self.holes[x].f-marble.f != self.holes[x].g-marble.g): #if is legal move
                    if self.holes[x].marble == None: #if empty hole
                        selectables.append(self.holes[x])
                    else: #can skip?
                        checkf = self.holes[x].f + (self.holes[x].f-marble.f) #another scoot in the direction
                        checkg = self.holes[x].g + (self.holes[x].g-marble.g)


            for s in selectables:
                print s



b = Board(6)
b.hostGame()