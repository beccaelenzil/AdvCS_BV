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
        return "Player " + str(self.player) + "'s marble at (" + str(self.f) + ", " + str(self.g) + "), id is " + str(id(self))
    def __iadd__(self, coord): #add a coordinate tuple in the form coord = (f, g)
        self.f += coord[0]
        self.g += coord[1]
        self.update()
        return self # when you overload a function like iadd, you need to return self.

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
    def __repr__(self):
        return "(" + str(self.f) + ", " + str(self.g) + "), " + ("occupied by a " + str(self.marble.sphere.color) + " marble" if self.marble != None else " empty")

class Board:
    def __init__(self, players):
        self.players = players #number of players
        #the actual "wood" cylinder that is the board
        self.board = cylinder(pos = (0, 7, -.5), axis = (0, 0, .5), radius = 8, height = .5, material = materials.wood)

        #Start with an array of fakes, so there aren't any exceptions when iterating
        self.marbles = {}
        for f in range(-4, 12):
            for g in range(-4, 12):
                self.marbles[(f, g)] = Marble(f, g, None, True)

        #the top/bottom vertices of the triangles that are the initial locations of the marbles
        startPts = [(0, 0), (8, -1), (9, 0), (8, 8), (0, 9), (-1, 8)]
        #all legal moves of one space, in the form of (deltaF, deltaG)
        self.unitmoves = [(0, 1), (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1)]

        #make dummy holes for same reason
        self.holes = {}
        for f in range(-4, 12):
            for g in range(-4, 12):
                self.marbles[(f, g)] = Marble(f, g, 0, True)

        #make REAL holes
        #these nested loops go in concentric circles around the origin, decreasing radius every time, initializing real holes
        for startf in range(4):
            loc = (startf, 4)
            for move in self.unitmoves:
                for n in range(4 - startf):
                    self.holes[loc] = Hole(loc[0], loc[1], None, False)
                    loc = (loc[0] + move[0], loc[1] + move[1]) #move to next hole position
        self.holes[(4, 4)] = Hole(4, 4, None, False) #this is the special case of the center hole that the loop doesn't cover

        for p in range(6): #create each player's marbles
            for f in range(4): #these nested loops create the triangles of balls around the perimeter
                for g in range(4 - f):
                    actualF = startPts[p][0] + f * (-1 if p%2==1 else 1)
                    actualG = startPts[p][1] + g * (-1 if p%2==1 else 1)
                    self.marbles[(actualF, actualG)] = Marble(actualF, actualG, p, False)
                    self.holes[(actualF, actualG)] = Hole(actualF, actualG, self.marbles[(actualF, actualG)], False)

    def hostGame(self):
        #to know what to deselect
        prevSelectedShape = None
        prevSelectedColor = None

        colors = [color.red, color.orange, color.yellow, color.green, color.blue, color.white]
        turn = 0
        isJumping = False #flag for if player is on a jumping run, if so use same marble
        while(self.whoWon() == -1):
            print "turn is " + str(turn)
            canExit = False #make sure that something is selected when user clicks

            #----choose a marble------

            if not isJumping: #first turn, marble needs to be selected
                #wait for click
                while not (scene.mouse.clicked and canExit):
                    if scene.mouse.clicked:
                        scene.mouse.getclick()
                    p = scene.mouse.pick
                    if prevSelectedShape != p: #if the cursor is over a new marble or no longer over one
                        if prevSelectedShape != None: #revert old selection to original color
                            prevSelectedShape.color = prevSelectedColor
                            canExit = False
                        if p != None and p.__class__ is sphere and\
                            abs(p.color[0] - colors[turn][0]) + abs(p.color[1] - colors[turn][1]) + abs(p.color[2] - colors[turn][2]) < .001: #if a marble is selected
                            prevSelectedColor = p.color #backup color to variable
                            p.color = color.magenta #highlight
                            prevSelectedShape = p
                            canExit = True
                    sleep(0.01) #to allow time to render
                obj = scene.mouse.pick
                obj.color = prevSelectedColor
                scene.mouse.getclick()

                marble = [self.marbles[key] for key in self.marbles\
                              if (False if self.marbles[key].isFake else self.marbles[key].sphere == obj)][0]

            #-------choose a hole---------

            #see if are within 1 unit in both directions, and also check to see if diff is not same for both b/c (-1,-1), (0,0), and (1, 1) aren't legal
            selectables = []
            for test in self.unitmoves:
                if (self.holes[(marble.f + test[0], marble.g + test[1])].marble == None if (marble.f + test[0], marble.g + test[1]) in self.holes else False)\
                        and not isJumping:
                    selectables.append(self.holes[(marble.f + test[0], marble.g + test[1])])
                if self.holes[(marble.f + 2*test[0], marble.g + 2*test[1])].marble == None if (marble.f + 2*test[0], marble.g + 2*test[1]) in self.holes else False:
                    selectables.append(self.holes[(marble.f + 2*test[0], marble.g + 2*test[1])])


            shapes = [x.shape for x in selectables] #for comparison with selected object

            prevSelectedShape = None
            canExit = False
            while not (scene.mouse.clicked and canExit): #until
                if scene.mouse.clicked:
                    scene.mouse.getclick()
                p = scene.mouse.pick
                if prevSelectedShape != p: #if the cursor is over a new hole or no longer over one
                    if prevSelectedShape != None: #revert old selection to original color
                        prevSelectedShape.color = color.black
                        canExit = False
                    if p != None and p in shapes:
                        p.color = color.yellow #highlight
                        prevSelectedShape = p
                        canExit = True
                sleep(0.01) #to allow time to render
            obj = scene.mouse.pick
            scene.mouse.getclick()
            hole = [self.holes[key] for key in self.holes if self.holes[key].shape == obj][0]

            oldHole = [self.holes[key] for key in self.holes if self.holes[key].f == marble.f and self.holes[key].g == marble.g][0]
            oldHole.shape.color = color.black
            oldHole.marble = None

            #move stuff (old way)
            #marble.f = hole.f
            #marble.g = hole.g
            #hole.marble = marble
            #hole.shape.color = color.black
            #marble.update()

            #animation sequence -- marble turning to None???
            incs = 100 #fraction of distance to incriment each time
            time = 2 #seconds to take to move
            vel = (1.0*(hole.f-marble.f)/incs, 1.0*(hole.g-marble.g)/incs)
            #print marble
            for i in range(incs):
                print marble
                #marble.f += vel[0] # It worked if put the functionality of iadd right here,
                #marble.g += vel[1] #so I knew it was an issue with iadd
                marble += vel
                sleep(1.0*time/incs)

            if max([abs(hole.f - oldHole.f), abs(hole.g - oldHole.g)]) == 2: #if it jumped
                isJumping = True
                continue #player gets another turn

            if self.players==2:
                turn += 3
            elif self.players==4:
                turn += 2 if turn%3==0 else 1
            else:
                turn += 1
            turn %= 6

    def whoWon(self):
        return -1

b = Board(2)
b.hostGame()