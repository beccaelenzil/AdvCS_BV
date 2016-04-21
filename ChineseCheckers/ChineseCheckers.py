from visual import *
import math
import random
import sys
from munkres import Munkres, print_matrix

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
    def move(self, target):
        incs = 10 #fraction of distance to incriment each time
        height = 2 #how far up the ball goes
        disp = (1.0*(target[0]-self.f), 1.0*(target[1]-self.g))
        vel = ((disp[1]-disp[0])/2.0/incs, (disp[1]+disp[0])*math.sqrt(3)/2/incs, 0)
        currPos = [(self.g-self.f)/2.0, (self.g+self.f)*math.sqrt(3)/2]
        a = -1.0*height/((incs/2)**2) #factor for jump parabola
        for i in range(incs):
            currPos[0] += vel[0]
            currPos[1] += vel[1]
            self.sphere.pos = (currPos[0], currPos[1], a*i*(i-incs))
            sleep(0.01)
        self += disp #formally register the movement
    def coord(self):
        return (self.f, self.g)

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
    def coord(self):
        return (self.f, self.g)
    def __repr__(self):
        return "(" + str(self.f) + ", " + str(self.g) + "), " + ("occupied by a " + str(self.marble.sphere.color) + " marble" if self.marble != None else " empty")

class Board:
    def __init__(self, players, ncPlayers):
        self.nPlayers = players #number of players
        self.ncPlayers = ncPlayers #number of computer players

        if ncPlayers > players:
            print "too many computer players!!"
            sys.exit()

        self.playerSets = [[0, 3], [0, 1, 3, 4], [0, 1, 2, 3, 4, 5]] #the active player #s for 2, 4, and 6 players
        self.cPlayers = [3]#random.sample(self.playerSets[players/2-1], ncPlayers) #indices of computer players

        #the actual "wood" cylinder that is the board
        self.board = cylinder(pos = (0, 7, -.5), axis = (0, 0, .5), radius = 8, height = .5, material = materials.wood)

        #Start with an array of fakes, so there aren't any exceptions when iterating
        self.marbles = {}
        for f in range(-4, 12):
            for g in range(-4, 12):
                self.marbles[(f, g)] = Marble(f, g, None, True)

        #the top/bottom vertices of the triangles that are the initial locations of the marbles
        self.startPts = [(0, 0), (8, -1), (9, 0), (8, 8), (0, 9), (-1, 8)]
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
                    actualF = self.startPts[p][0] + f * (-1 if p%2==1 else 1)
                    actualG = self.startPts[p][1] + g * (-1 if p%2==1 else 1)
                    self.marbles[(actualF, actualG)] = Marble(actualF, actualG, p, False)
                    self.holes[(actualF, actualG)] = Hole(actualF, actualG, self.marbles[(actualF, actualG)], False)

        #for reference by computer players
        self.targets = [[]] * 6
        for p in range(6):
            for f in range(4): #these nested loops create the triangles of balls around the perimeter
                for g in range(4 - f):
                    targetP = (p+3)%6
                    actualF = self.startPts[targetP][0] + f * (-1 if targetP%2==1 else 1)
                    actualG = self.startPts[targetP][1] + g * (-1 if targetP%2==1 else 1)
                    self.targets[p].append((actualF, actualG))


    def hostGame(self):
        #to know what to deselect
        prevSelectedShape = None
        prevSelectedColor = None

        colors = [color.red, color.orange, color.yellow, color.green, color.blue, color.white]
        turn = 0
        isJumping = False #flag for if player is on a jumping run, if so use same marble
        scrtext = label(text='', align='center', pos = (-11, 12, 0))
        self.exitTurn = False #flag for when user is done with jumping turn

        while(self.whoWon() == -1):
            scrtext.text = 'Player ' + str(self.playerSets[self.nPlayers/2-1].index(turn)+1) + "'s turn" + ('\nPress any key to exit turn' if isJumping else '')
            scrtext.color = colors[turn]
            canExit = False #make sure that something is selected when user clicks

            if turn in self.cPlayers: #it is a computer's turn
                self.computerMove(turn)

                if self.nPlayers==2:
                    turn += 3
                elif self.nPlayers==4:
                    turn += 1 if turn%3==0 else 2
                else:
                    turn += 1
                turn %= 6
                continue

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
                scene.mouse.getclick()

                marble = [self.marbles[key] for key in self.marbles\
                              if (False if self.marbles[key].isFake else self.marbles[key].sphere == obj)][0]

            #-------choose a hole---------

            #see if are within 1 unit in both directions, and also check to see if diff is not same for both b/c (-1,-1), (0,0), and (1, 1) aren't legal
            selectables = []
            for test in self.unitmoves:
                if (self.holes[(marble.f + test[0], marble.g + test[1])].marble == None if (marble.f + test[0], marble.g + test[1]) in self.holes else False):
                    if not isJumping:
                        selectables.append(self.holes[(marble.f + test[0], marble.g + test[1])])
                #if there is a marble one 'test' over, check 2 over
                elif self.holes[(marble.f + 2*test[0], marble.g + 2*test[1])].marble == None if (marble.f + 2*test[0], marble.g + 2*test[1]) in self.holes else False:
                    selectables.append(self.holes[(marble.f + 2*test[0], marble.g + 2*test[1])])

            shapes = [x.shape for x in selectables] #for comparison with selected object

            prevSelectedShape = None
            canExit = False
            while not ((scene.mouse.clicked and canExit) or self.exitTurn):
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

            if not self.exitTurn: #if not exiting turn because of user key during hole select
                obj = scene.mouse.pick
                scene.mouse.getclick()
                theHoles = [self.holes[key] for key in self.holes if self.holes[key].shape == obj]
                if len(theHoles) == 0: #weird bug - retry turn
                    self.exitTurn = False
                    isJumping = False
                    scene.unbind('keydown', self.keycb)
                    scene.waitfor('keyup')
                    oldHole.shape.color = color.black
                    continue
                hole = theHoles[0]
                hole.marble = marble

                oldHole = [self.holes[key] for key in self.holes if self.holes[key].f == marble.f and self.holes[key].g == marble.g][0]
                oldHole.shape.color = color.black
                oldHole.marble = None

                marble.move((hole.f, hole.g))

                if max([abs(hole.f - oldHole.f), abs(hole.g - oldHole.g)]) == 2: #if it jumped
                    isJumping = True
                    scene.bind('keydown', self.keycb)
                    continue #player gets another turn

            #only revert if not still jumping
            marble.sphere.color = colors[marble.player]

            if self.nPlayers==2:
                turn += 3
            elif self.nPlayers==4:
                turn += 1 if turn%3==0 else 2
            else:
                turn += 1
            turn %= 6

            if self.exitTurn: #key triggered
                self.exitTurn = False
                isJumping = False
                scene.unbind('keydown', self.keycb)
                scene.waitfor('keyup')
                oldHole.shape.color = color.black

    def whoWon(self):
        #for player (p+3)%6
        for p in range(6):
            won = True
            for f in range(4):
                for g in range(4 - f):
                    actualF = self.startPts[p][0] + f * (-1 if p%2==1 else 1)
                    actualG = self.startPts[p][1] + g * (-1 if p%2==1 else 1)
                    hole = self.holes[(actualF, actualG)]
                    if (hole.marble.player != ((p+3)%6) if hole.marble != None else True):
                        won = False
                        break
                if not won:
                    break
            if won:
                print str((p+3)%6) + " wins"
                return (p+3)%6
        return -1

    def keycb(self, evt):
        self.exitTurn = True

    def computerMove(self, p):
        #get marbles relevant to player
        pmarbles = []
        for key in self.marbles:
            if self.marbles[key].player == p and not self.marbles[key].sphere == None: #make sure its not fake
                pmarbles.append(self.marbles[key])

        marblesPos = [self.cart(m.coord()) for m in pmarbles] #cartesian coord of each marble

        #start by choosing target hole for each ball, minimizing error

        #make array of squared distance from each marble to each hole
        d = [[0.0] * 10] * 10
        for marble in range(10):
            for hole in range(10):
                d[marble][hole] = self.sqd(self.cart(pmarbles[marble].coord()),\
                                           self.cart(self.targets[p][hole]))

        #assign holes
        m = Munkres()
        idxs = m.compute(d)
        idxs.sort() #sort by marble
        targets = [self.targets[p][idx[1]] for idx in idxs] #get hole target for each marble, not to be comfused with self.targets

        print self.error(marblesPos, targets)

        #test each move for each marble
        visitedSpaces = [] #to make sure there isn't an infinite loop
        paths = [[]] * 10 #for each marble, a list of lists of tuples that show the path
        for marble in range(10):
            for u in self.unitmoves:
                coord = (pmarbles[marble].f + u[0], pmarbles[marble].g + u[1])
                if (self.holes[coord].marble == None if coord in self.holes else False):
                    paths[marble].append([coord])
            #recursively check for jumps
            #print "Branching marble " + str(marble)
            self.branchMoves(pmarbles[marble], paths[marble], [pmarbles[marble].coord()], visitedSpaces)

        lowestError = 10000000 #keep track of current record
        lowestMarble = 0
        lowestPath = None
        for i in range(10): #for each marble
            bk = marblesPos[i] #to save value before experimenting
            for path in paths[i]:
                loc = path[-1]#(sum([x[0] for x in path]) + pmarbles[i].f, sum([x[1] for x in path]) + pmarbles[i].g) #get location in world coords
                marblesPos[i] = self.cart(loc)
                e = self.error(marblesPos, targets)
                if e < lowestError:
                    lowestError = e
                    lowestMarble = i
                    lowestPath = path
            marblesPos[i] = bk
        print "Lowest error: " + str(lowestError)
        print "Lowest path: " + str(lowestPath)
        print "Lowest marble: " + str(pmarbles[lowestMarble]) + ", index is " + str(lowestMarble)
        print paths[lowestMarble]
        #targets in f and g
        loc = lowestPath[-1]
        print "final move: " + str(loc)
        for move in lowestPath:
            pmarbles[lowestMarble].move(move)

    def error(self, marblesPos, targets):
        e = 0.0
        for i in range(10):
            e += self.sqd(marblesPos[i], targets[i])
        return e

    def branchMoves(self, marble, paths, currPath, visitedSpaces):
        currLoc = currPath[-1] #world coords
        #print "currLoc is " + str(currLoc)
        visitedSpaces.append(currLoc) #avoid infinite loops
        #print currPath
        paths.append([x for x in currPath]) #register as a valid space to move to (mutability fix?)
        #print paths
        for u in self.unitmoves: #check for other spaces surrounding
            coord1 = (currLoc[0] + u[0], currLoc[1] + u[1]) #one and two units in this direction, relative to marble
            coord2 = (currLoc[0] + 2*u[0], currLoc[1] + 2*u[1])
            if not coord2 in visitedSpaces\
                    and (self.holes[coord2].marble == None if coord2 in self.holes else False)\
                    and (self.holes[coord1].marble != None if coord1 in self.holes else False): #make sure is unvisited by recursion, empty, and has marble in between
                #print "coord2 is " + str(coord2)
                currPath.append(coord2)
                #print currPath
                self.branchMoves(marble, paths, currPath, visitedSpaces)
                del currPath[-1] #delete last element to keep track

    def cart(self, coord):
        return ((coord[1]-coord[0])*.5, (coord[1]+coord[0])*math.sqrt(3)/2)

    def sqd(self, a, b): #squared distance between tuples a and b
        return (a[0]-b[0])**2 + (a[1]-b[1])**2

    def matadd(self, a, c):#add a scalar to a 2d array
        ret = [[0.0] * len(a[0])] * len(a)
        for i in range(len(a)):
            for j in range(len(a[0])):
                ret[i][j] = a[i][j] + c
        return ret

def getIntInput(string, range):
    reply = 0
    valueOk = False
    while not valueOk:
        valueOk = True
        try:
            reply = int(input(string))
        except:
            valueOk = False
        if not reply in range:
            valueOk = False
            print 'Must be one of ' + str(range)
    return reply

def playGame():
    #players = getIntInput("How many players?", range(2, 7, 2)) #2, 4, or 6 players
    #cPlayers = getIntInput("How many AIs?", range(0, players+1)) #can be 0 to all AI players
    b = Board(2, 1)
    b.hostGame()

playGame()