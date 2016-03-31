from visual import *
from visual_common import primitives
import math

class Marble:
    def __init__(self, f, g, player, isFake):
        """
        coordinate system:
        origin at bottom circle
        (units moving diagonal northwest (f), units moving diagonal northeast (g))
        player is int from 0 to 5
        isFake is bool, if true then object is a dummy marble that doesn't actually exist, used for avoiding
            function call to None
        """
        self.f = f
        self.g = g
        self.player = player
        self.colors = [color.red, color.orange, color.yellow, color.green, color.blue, color.white]
        self.isFake = isFake
        if not isFake:
            self.sphere = sphere(pos = ((g-f)/2.0, (g+f)*math.sqrt(3)/2, 0), radius=0.3, color = self.colors[player])
        else:
            self.sphere = None

    def update(self): #re-render the sphere to account for changes to position
        self.sphere.pos = ((self.g-self.f)/2.0, (self.g+self.f)*math.sqrt(3)/2, 0)
    def __repr__(self):
        return "Player " + str(self.player) + "'s marble at (" + str(self.f) + ", " + str(self.g) + ")"
    def __iadd__(self, coord): #add a coordinate tuple in the form coord = (f, g)
        self.f += coord[0]
        self.g += coord[1]
        self.update()

class Hole:
    def __init__(self, f, g, marble, isFake):
        """
        coordinate system:
        origin at bottom circle
        (units moving diagonal northwest (f), units moving diagonal northeast (g))
        marble is a Marble object that occupies this hole, or None if empty
        isFake is bool, if true then object is a dummy hole that doesn't actually exist, used for avoiding
            function call to None
        """
        self.f = f
        self.g = g
        self.marble = marble
        if not isFake:
            self.shape = cylinder(pos = ((self.g-self.f)/2.0, (self.g+self.f)*math.sqrt(3)/2, -.295), axis = (0, 0, .3), radius = 0.3, height = .3, color = color.black)
        else:
            self.shape = None
    def highlight(self, hl): #helper func for when cursor hovers over hole
        if hl:
            self.shape.color = color.yellow
        else:
            self.shape.color = color.black
    def __repr__(self):
        return "(" + str(self.f) + ", " + str(self.g) + "), " + ("occupied by a " + str(self.marble.sphere.color) + " marble" if self.marble != None else " empty")

class Board:
    def __init__(self, players):
        self.players = players #number of players
        #the actual "wood" cylinder that is the board
        self.board = cylinder(pos = (0, 7, -.5), axis = (0, 0, .5), radius = 8, height = .5, material = materials.wood)

        #Start with an array of fakes, so there aren't any exceptions when iterating
        self.marbles = [[Marble(0, 0, 0, True)] * 12] * 12 #put fake marbles in array

        #the top/bottom vertices of the triangles that are the initial locations of the marbles
        startPts = [(0, 0), (8, -1), (9, 0), (8, 8), (0, 9), (-1, 8)]
        #all legal moves of one space, in the form of (deltaF, deltaG)
        self.unitmoves = [(0, 1), (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1)]

        #make dummy holes for same reason
        self.holes = [[Hole(f, g, None, True) for f in range(12)] for g in range(12)]

        #make REAL holes
        #these nested loops go in concentric circles around the origin, decreasing radius every time, initializing real holes
        for startf in range(4):
            loc = (startf, 4)
            for move in self.unitmoves:
                for n in range(4 - startf):
                    self.holes[loc[0]][loc[1]] = Hole(loc[0], loc[1], None, False)
                    loc = (loc[0] + move[0], loc[1] + move[1]) #move to next hole position
        self.holes[4][4] = Hole(4, 4, None, False) #this is the special case of the center hole that the loop doesn't cover

        for p in range(6): #create each player's marbles
            for f in range(4): #these nested loops create the triangles of balls around the perimeter
                for g in range(4 - f):
                    self.marbles[f][g] = Marble(startPts[p][0] + f * (-1 if p%2==1 else 1), startPts[p][1] + g * (-1 if p%2==1 else 1), p, False)
                    self.holes[f][g] = Hole(f, g, self.marbles[f][g], False)

    def hostGame(self):
        #so we know what to deselect
        prevSelectedShape = None
        prevSelectedColor = None
        #whose turn is it anyways
        turn = 0
        while(True):
            #wait for click
            while not scene.mouse.clicked:
                p = scene.mouse.pick
                if prevSelectedShape != p: #if the cursor is over a new marble or no longer over one
                    if prevSelectedShape != None: #revert old selection to original color
                        prevSelectedShape.color = prevSelectedColor
                    if p != None and "sphere" in str(p): #if a marble is selected
                        prevSelectedColor = p.color #backup color to variable
                        p.color = color.magenta #highlight
                        prevSelectedShape = p
                sleep(0.01) #to allow time to render
            print "clicked"
            obj = scene.mouse.pick
            scene.mouse.getclick()

            #here on out in development

            print obj
            print ""

            for m in self.marbles:
                for mm in m:
                    if not mm.isFake:
                        print mm
                        print mm.sphere

            themarbles = [self.marbles[x/12][x%12] for x in range(144) if self.marbles[x/12][x%12].sphere==obj]
            if len(themarbles)==0:
                print "not a marble"
                continue
            marble = themarbles[0]
            print marble
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