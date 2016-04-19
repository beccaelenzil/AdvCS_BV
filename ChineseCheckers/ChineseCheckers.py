from visual import *
import math
import random
import sys

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
    def __init__(self, players, ncPlayers):
        self.players = players #number of players
        self.ncPlayers = ncPlayers #number of computer players

        if ncPlayers > players:
            print "too many computer players!!"
            sys.exit()

        playerSets = [[0, 3], [0, 1, 3, 4], [0, 1, 2, 3, 4, 5]] #the active player #s for 2, 4, and 6 players
        self.cPlayers = random.sample(playerSets[players/2], ncPlayers) #indices of computer players

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
                    self.targets[p].append(self.cart((actualF, actualG)))


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
            scrtext.text = 'Player ' + str(turn+1) + "'s turn"
            scrtext.color = colors[turn]
            canExit = False #make sure that something is selected when user clicks

            if turn in self.cPlayers:

                self.computerMove(turn)

                if self.players==2:
                    turn += 3
                elif self.players==4:
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
                obj.color = prevSelectedColor
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

            if not self.exitTurn:
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

            if self.players==2:
                turn += 3
            elif self.players==4:
                turn += 1 if turn%3==0 else 2
            else:
                turn += 1
            turn %= 6

            if self.exitTurn:
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
        #get marbles
        pmarbles = []
        pholes = []
        for key in self.marbles:
            if self.marbles[key].player == p:
                pmarbles.append(self.marbles[key])
                pholes.append(self.holes[key])

        #start by choosing target hole for each ball, minimizing error

        #make array of squared distance from each marble to each hole
        d = [[0.0] * 10] * 10
        for hole in range(10):
            for marble in range(10):
                d[hole][marble] = self.sqd(self.cart((pmarbles[marble].f, pmarbles[marble].g)),\
                                           self.cart((pholes[hole].f, pholes[hole].g)))

        #find most efficient pairing with Hungarian algorithm
        #step 1 - subtract row minimums
        for row in range(10):
            for col in range(10):
                d[row][col] -= min(d[row])
        #step 2 - subtract col minimums
        for row in range(10):
            for col in range(10):
                d[row][col] -= min([d[r][col] for r in range(10)])

        #steps 3-5 - make lines
        rowLines = [False] * 10 #if each row/col has line
        colLines = [False] * 10
        rowZeros = [0] * 10 #how many zeros are in each row/col
        colZeros = [0] * 10
        while True: #condition appears midway
            for row in range(10):
                rowZeros[row] = sum([d[row][col]==0 for col in range(10)])
            for col in range(10):
                colZeros[col] = sum([d[row][col]==0 for row in range(10)])

            numZeros = sum(rowZeros) #could be colZeros, just finding how many total
            while numZeros > 0: #cover all zeros most efficiently
                idx = (rowZeros + colZeros).index(max(rowZeros + colZeros))
                if idx < 10: #is a row line
                    rowLines[idx] = True
                    rowZeros[idx] = 0   # no uncrossed zeros in this col
                    for x in range(10): # subtract zeros in this row from col register
                        if d[row][x] == 0:
                            rowZeros[x] -= 1
                else: #a column line
                    colLines[idx-10] = True
                    colZeros[idx-10] = 0
                    for x in range(10):
                        if d[x][col] == 0:
                            colZeros[x] -= 1
                numZeros -= max(rowZeros + colZeros)

            if sum(rowLines + colLines) >= 10: #total number of covering lines
                break

            #smallest entry not covered by any line
            lowval = max([max(d[row]) for row in range(10)])
            for row in range(10):
                if rowLines[row]:
                    continue
                for col in range(10):
                    if colLines[col]:
                        continue
                    if d[row][col] < lowval:
                        lowval = d[row][col]

            #subtract from each uncovered row
            for row in range(10): #subtract from each uncovered row
                if rowLines[row]:
                    continue
                for col in range(10):
                    d[row][col] -= lowval
            for col in range(10): #add to each covered col
                if not colLines[col]:
                    continue
                for row in range(10):
                    d[row][col] += lowval

        #get final combos of zeros
        zerosPerRow = [] * 10
        for row in range(10):
            zerosPerRow[row] = sum([1 for x in range(10) if d[row][x]==0])
        zerosPerCol = [] * 10
        for col in range(10):
            zerosPerCol[col] = sum([1 for x in range(10) if d[x][col]==0])

        #find set of 10 zeros unique to cols and rows
        lens = [0] * 10

    def error(self, marblesPos, p):
        e = 0.0
        for i in range(10):
            e += self.sqd(marblesPos[i], self.targets[p][i])
        return e

    def cart(self, f, g): #convert to cartesian coords
        return ((g-f)*.5, (g+f)*math.sqrt(3)/2)

    def sqd(self, a, b): #squared distance between tuples a and b
        return (a[0]-b[0])**2 + (a[1]-b[1])**2

    def matadd(self, a, c):#add a scalar to a 2d array
        ret = [[0.0] * len(a[0])] * len(a)
        for i in range(len(a)):
            for j in range(len(a[0])):
                ret[i][j] = a[i][j] + c
        return ret

b = Board(2, 1)
b.hostGame()