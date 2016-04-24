from visual import * #vpython library
import math #other misc imports
import random
import sys

"""
Note on coordinate system for whole program:
Origin is at bottom circle
Coordinate tuple format:
(units in the northwest direction, units in the northeast direction) = (f, g)
"""
class Marble: #represents a single marble
    def __init__(self, f, g, player, isFake):

        """
        params:
        f and g are the coordinates, explained above
        player is the index of the player that this marble belongs to, int from 0 to 5
        colors is a static array, the marble color for each player index
        isFake is bool, if true then object is a dummy marble that doesn't actually exist, used for avoiding
            function call to None
        """
        self.f = f
        self.g = g
        self.player = player
        self.colors = [color.red, color.orange, color.yellow, color.green, color.blue, color.white]
        self.isFake = isFake

        #some constants for animation
        self.incs = 10 #how many movements to divide animation into
        self.height = 2 #how far up the ball goes

        if not isFake: #if it is a real marble, create a sphere (calculations change (f, g) to cartesian coords)
            self.sphere = sphere(pos = ((g-f)/2.0, (g+f)*math.sqrt(3)/2, 0), radius=0.3, color = self.colors[player])
        else:
            self.sphere = None

    def update(self): #re-render the sphere to account for changes to position
        self.sphere.pos = ((self.g-self.f)/2.0, (self.g+self.f)*math.sqrt(3)/2, 0)
    def __repr__(self): #marble description, for debugging
        return "Player " + str(self.player) + "'s marble at (" + str(self.f) + ", " + str(self.g) + "), id is " + str(id(self))
    def __iadd__(self, coord): #add a coordinate tuple to this marble's position
        self.f += coord[0]
        self.g += coord[1]
        self.update()
        return self # when you overload a function like iadd, you need to return self.
    def move(self, target): #move marble to a target (f, g) location
        disp = (1.0*(target[0]-self.f), 1.0*(target[1]-self.g)) #displacement vector in (f, g)
        vel = ((disp[1]-disp[0])/2.0/self.incs, (disp[1]+disp[0])*math.sqrt(3)/2/self.incs, 0) #velocity (how far to move each iteration), in (f, g)
        currPos = [(self.g-self.f)/2.0, (self.g+self.f)*math.sqrt(3)/2] #current position (cartesian)
        a = -1.0*self.height/((self.incs/2)**2) #factor for jump quadratic
        for i in range(self.incs):
            currPos[0] += vel[0]
            currPos[1] += vel[1]
            self.sphere.pos = (currPos[0], currPos[1], a*i*(i-self.incs)) #update sphere position, with parabolic shape for jump motion
            sleep(0.05) #time to update
        self += disp #formally register the movement in f and g
    def coord(self): #return position as a tuple coordinate (f, g)
        return (self.f, self.g)

class Hole: #represents a single hole
    def __init__(self, f, g, marble, isFake):
        """
        coordinate system: described at top
        f and g are namesake coords
        marble is a Marble object that occupies this hole, or None if empty
        isFake is bool, if true then this object is a dummy hole that doesn't actually exist, used for avoiding
            function call to None
        """
        self.f = f
        self.g = g
        self.marble = marble
        if not isFake: #if real, create a shallow cylinder at this (f, g)
            self.shape = cylinder(pos = ((self.g-self.f)/2.0, (self.g+self.f)*math.sqrt(3)/2, -.295), axis = (0, 0, .3), radius = 0.3, height = .3, color = color.black)
        else:
            self.shape = None
    def coord(self): #get coordinate tuple in (f, g)
        return (self.f, self.g)
    def __repr__(self): #string representation, for debugging
        return "(" + str(self.f) + ", " + str(self.g) + "), " + ("occupied by a " + str(self.marble.sphere.color) + " marble" if self.marble != None else " empty")

class Board: #class that contains variables and functions for board state and gameplay. The majority of the program
    def __init__(self, players, ncPlayers):
        self.nPlayers = players #number of players
        self.ncPlayers = ncPlayers #number of computer players

        if ncPlayers > players: #check input validity
            print "too many computer players!!"
            sys.exit()

        # The indices of active players for 2, 4, and 6 players respectively.
        # Since 1, 3, and 5 players not possible, should be referenced as self.playerSets[player/2-1]
        self.playerSets = [[0, 3], [0, 1, 3, 4], [0, 1, 2, 3, 4, 5]]

        # Array of indices of computer players. Randomly chooses requested number of computer players from array of active players
        self.cPlayers = random.sample(self.playerSets[players/2-1], ncPlayers)

        #the actual "wood" cylinder that is the board
        self.board = cylinder(pos = (0, 7, -.5), axis = (0, 0, .5), radius = 8, height = .5, material = materials.wood)

        self.marbles = {} #dictionary of marbles, where key is coordinate tuple in (f, g)
        self.holes = {} #equivalent for holes

        #Hard to explain reference arrays for generating board and marbles:
        #the top/bottom vertices of the triangles that are the initial locations of the marbles
        self.startPts = [(0, 0), (8, -1), (9, 0), (8, 8), (0, 9), (-1, 8)]
        #array of legal moves of one space, in the form of (deltaF, deltaG)
        self.unitmoves = [(0, 1), (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1)]

        #make  holes
        #these nested loops go in concentric hexagons around the center hole, decreasing radius every time, initializing real holes
        for startf in range(4): #radius of hexagon
            loc = (startf, 4) #start location
            for move in self.unitmoves: #go 4-startf units in each of the 6 directions to make concentric hexagons
                for n in range(4 - startf):
                    self.holes[loc] = Hole(loc[0], loc[1], None, False) #create a real hole
                    loc = (loc[0] + move[0], loc[1] + move[1]) #move to next hole position
        self.holes[(4, 4)] = Hole(4, 4, None, False) #this is the special case of the center hole that the loop doesn't cover

        self.targets = [[] for i in range(6)] #target locations for each player (list comp. is mutability bug fix)
        #these nested loops create the triangles of balls around the perimeter
        for p in range(6): #create each player's marbles
            for f in range(4): #relative (f, g) coordinates of the players' triangles
                for g in range(4 - f):
                    actualF = self.startPts[p][0] + f * (-1 if p%2==1 else 1) #world coords
                    actualG = self.startPts[p][1] + g * (-1 if p%2==1 else 1)
                    self.marbles[(actualF, actualG)] = Marble(actualF, actualG, p, False) #create holes, marbles, and add position to targets array for later use by AI
                    self.holes[(actualF, actualG)] = Hole(actualF, actualG, self.marbles[(actualF, actualG)], False)
                    self.targets[(p+3)%6].append((actualF, actualG)) #for opposite player

    def hostGame(self): #play the game

        #UI variables
        #to know what to deselect
        prevSelectedShape = None
        prevSelectedColor = None

        #indexing of colors for each player
        colors = [color.red, color.orange, color.yellow, color.green, color.blue, color.white]
        turn = 0 #whose turn it is
        isJumping = False #flag for if player is on a jumping run, if so use same marble
        scrtext = label(text='', align='center', pos = (-11, 12, 0)) #heads-up text in corner of screen
        self.exitTurn = False #flag for when user is done with jumping turn

        while(self.whoWon() == -1): #keep taking turns until someone wins
            #say whose turn it is on display
            scrtext.text = 'Player ' + str(self.playerSets[self.nPlayers/2-1].index(turn)+1)\
                           + "'s turn" + (" (computer)" if turn in self.cPlayers else " (human)")\
                           + ('\nPress any key to exit turn' if isJumping else '')
            scrtext.color = colors[turn] #set text color to match player
            canExit = False #make sure that something is selected when user clicks

            if turn in self.cPlayers: #it is a computer's turn

                self.computerMove(turn) #call function to take computer's turn

                #advance to next player's turn, incrementing depends on how many players there are
                if self.nPlayers==2:
                    turn += 3
                elif self.nPlayers==4:
                    turn += 1 if turn%3==0 else 2
                else:
                    turn += 1
                turn %= 6

                sleep(0.5) #wait a bit before next turn
                continue #skip rest of loop (regular player's turn)

            #----choose a marble------

            if not isJumping: #if this is first movement, and therefore a marble needs to be selected
                #wait for click and object to be selected
                while not (scene.mouse.clicked and canExit):
                    if scene.mouse.clicked: #if there's and old click pending, get rid of it
                        scene.mouse.getclick()
                    p = scene.mouse.pick #find object cursor is pointing at
                    if prevSelectedShape != p: #if the cursor is over a new object or no longer over one
                        if prevSelectedShape != None: #revert old selection to original color
                            prevSelectedShape.color = prevSelectedColor
                            canExit = False #nothing selected anymore, so can't exit
                        #if the selected object is a sphere, and belongs to this player
                        if p != None and p.__class__ is sphere and\
                            abs(p.color[0] - colors[turn][0]) + abs(p.color[1] - colors[turn][1]) + abs(p.color[2] - colors[turn][2]) < .001: #if a marble is selected
                            prevSelectedColor = p.color #backup color to variable
                            p.color = color.magenta #highlight
                            prevSelectedShape = p #backup shape object
                            canExit = True #object selected, so ok to exit
                    sleep(0.01) #to allow time to render
                #get selected object
                obj = scene.mouse.pick
                #acknowledge click
                scene.mouse.getclick()

                #get the marble object that was selected
                marble = [self.marbles[key] for key in self.marbles\
                              if (False if self.marbles[key].isFake else self.marbles[key].sphere == obj)][0]

            #-------choose a hole---------

            #create list of candidate holes to move to (selectables)
            #see if are within 1 unit in both directions, and also check to see if coords are not same for both b/c (-1,-1), (0,0), and (1, 1) aren't legal
            selectables = []
            for test in self.unitmoves: #check in each direction
                #if hole in this direction exists and is vacant
                if (self.holes[(marble.f + test[0], marble.g + test[1])].marble == None if (marble.f + test[0], marble.g + test[1]) in self.holes else False):
                    if not isJumping: #can't take unit move if on jumping streak
                        selectables.append(self.holes[(marble.f + test[0], marble.g + test[1])]) #register as legal move
                #Check if jump possible
                #Jump legal if hole 1 space over is occupied and hole 2 spaces over is vacant
                elif self.holes[(marble.f + 2*test[0], marble.g + 2*test[1])].marble == None if (marble.f + 2*test[0], marble.g + 2*test[1]) in self.holes else False:
                    selectables.append(self.holes[(marble.f + 2*test[0], marble.g + 2*test[1])]) #jump move is legal

            shapes = [x.shape for x in selectables] #array of actual cylinder objects, for comparison with selected object

            #same idea as before
            prevSelectedShape = None
            canExit = False
            while not ((scene.mouse.clicked and canExit) or self.exitTurn): #also check exitTurn flag to see if player done with jumping streak
                if scene.mouse.clicked: #get rid of old click if exists
                    scene.mouse.getclick()
                p = scene.mouse.pick
                if prevSelectedShape != p: #if the cursor is over a new hole or no longer over one
                    if prevSelectedShape != None: #revert old selection to original color
                        prevSelectedShape.color = color.black
                        canExit = False
                if p != None and p in shapes: #if selected hole is legal move
                    p.color = color.yellow #highlight
                    prevSelectedShape = p
                    canExit = True #hole selected, so can move
                sleep(0.01) #to allow time to render

            if not self.exitTurn: #if not exiting turn because of user key during hole select
                obj = scene.mouse.pick
                scene.mouse.getclick() #acknowledge click and get object
                #get the hole object that was selected - this array should be 1 long, but there's an occasional bug (dealt with below)
                theHoles = [self.holes[key] for key in self.holes if self.holes[key].shape == obj]
                if len(theHoles) == 0: #weird bug - retry turn
                    self.exitTurn = False
                    isJumping = False
                    try: #reset event listeners
                        scene.unbind('keydown', self.keycb)
                    except:
                        whatever = True
                    scene.waitfor('keyup')
                    oldHole.shape.color = color.black
                    continue #skip and try another turn
                hole = theHoles[0] #everything went ok, get the hole
                hole.marble = marble #register the hole's marble

                #empty and de-highlight old hole
                oldHole = [self.holes[key] for key in self.holes if self.holes[key].f == marble.f and self.holes[key].g == marble.g][0]
                oldHole.shape.color = color.black
                oldHole.marble = None

                #move the marble
                marble.move((hole.f, hole.g))

                #if this was a jumping move (i.e. it moved 2 units)
                if max([abs(hole.f - oldHole.f), abs(hole.g - oldHole.g)]) == 2:
                    isJumping = True #set flag
                    scene.bind('keydown', self.keycb) #set event listener for when user wants to exit
                    continue #player gets another turn

            #only revert to old color if not still jumping, otherwise leave highlighted
            marble.sphere.color = colors[marble.player]

            #advance to next player's turn, incrementing depends on how many players there are
            if self.nPlayers==2:
                turn += 3
            elif self.nPlayers==4:
                turn += 1 if turn%3==0 else 2
            else:
                turn += 1
            turn %= 6

            if self.exitTurn: #if the exit key was triggered
                self.exitTurn = False
                isJumping = False
                scene.unbind('keydown', self.keycb) #turn off listeners
                scene.waitfor('keyup') #wait for key release, so it doesn't throw another listener
                oldHole.shape.color = color.black #de-highlight old hole

        #loop ended, so someone won. Put victory message on display
        scrtext.text = "Player " + str(self.playerSets[self.nPlayers/2-1].index(self.whoWon())+1) + " wins!"

    #function to determine who won, if anyone (returns index of winning player, or -1 if no one won yet)
    def whoWon(self):
        #for player (p+3)%6
        for p in range(6): #check each player
            won = True #assume won until proven otherwise
            for f in range(4): #relative coordinates in target triangle to check
                for g in range(4 - f):
                    actualF = self.startPts[p][0] + f * (-1 if p%2==1 else 1)
                    actualG = self.startPts[p][1] + g * (-1 if p%2==1 else 1)
                    hole = self.holes[(actualF, actualG)]
                    #this hole should be occupied by the player's marble if they won, otherwise clear flag
                    if (hole.marble.player != ((p+3)%6) if hole.marble != None else True):
                        won = False
                        break
                if not won: #if this player didn't win, don't waste time checking other holes
                    break
            if won: #if they win, print console message and return index of winning player
                print str((p+3)%6) + " wins"
                return (p+3)%6
        return -1 #default value, if no one won

    def keycb(self, evt): #callback event handler for key press
        self.exitTurn = True #set flag to exit

    #take a turn for the AI
    def computerMove(self, p):
        #get marbles relevant to player
        pmarbles = []
        for key in self.marbles:
            if self.marbles[key].player == p and not self.marbles[key].sphere == None: #make sure its not fake
                pmarbles.append(self.marbles[key])

        marblesPos = [self.cart(m.coord()) for m in pmarbles] #cartesian coord of each marble

        #the target coordinate for the player, for reference in the error function.
        #this coord is not an actual spot on the board, but a point towards which all the marbles gravitate
        target = [(10, 10), (-2, 14), (-6, 10), (-2, -2), (10, -6), (14, -2)][p]

        #print information on current error
        print "-------------------"
        print "current error: " + str(self.error(marblesPos, target))

        #compile paths, an array of turns the player could take
        paths = []
        for marble in range(10): #for each marble
            for u in self.unitmoves: #first add the basic one unit moves
                coord = (pmarbles[marble].f + u[0], pmarbles[marble].g + u[1]) #target coord
                if (self.holes[coord].marble == None if coord in self.holes else False): #if this space is empty
                    paths.append([pmarbles[marble].coord(), coord]) #register as a valid move
            #recursively check for jumps with branchMoves function
            #First param is paths array to contribute to
            #Second is the current path it is exploring - starts with just the marble's coordinate
            #Third param is list of already visited spots, to avoid infinite loops
            self.branchMoves(paths, [pmarbles[marble].coord()], [])

        startE = self.error(marblesPos, target)
        lowestError = 10000000 #keep track of current record (initialized arbitrarily high)
        lowestPath = None #the best one so far
        for path in paths: #check each one
            marbleIdx = [x for x in range(10) if pmarbles[x].coord()==path[0]][0] #index of marble referenced in path
            loc = path[-1] #final destination
            bk = marblesPos[marbleIdx] #save old position value during testing
            marblesPos[marbleIdx] = self.cart(loc) #set to new hypothetical position
            e = self.error(marblesPos, target) #calculate new error for hypothetical situation
            if e < lowestError: #if this is the best one yet, save it
                lowestError = e
                lowestPath = path
            marblesPos[marbleIdx] = bk #revert to old valeu
        print "lowest error: " + str(lowestError) #print results
        print "lowest path: " + str(lowestPath)
        if lowestError > startE: #moving against negative gradient, stuck in local minimum
            #make a random move
            print "hit local minimum, picking random short move."
            lowestPath = random.choice([path for path in paths if len(path) <= 3]) #only short paths, 2 moves max
        theMarble = [m for m in pmarbles if m.coord() == lowestPath[0]][0] #get the marble to move
        del lowestPath[0] #get rid of now redundant marble position

        #targets in f and g
        loc = lowestPath[-1] #last element of path
        print "final move: " + str(loc)

        self.holes[theMarble.coord()].marble = None #register old hole as empty
        for move in lowestPath: #perform each move
            theMarble.move(move)
            sleep(0.2)
        self.holes[loc].marble = theMarble #register new hole as full

    #the squared error function for an array of cartesian marble locations (marblesPos), given a target tuple in (f, g)
    def error(self, marblesPos, target):
        e = 0.0
        for pos in marblesPos:
            e += self.sqd(pos, self.cart(target)) #add the squared distance of each marble
        return e

    def branchMoves(self, paths, currPath, visitedSpaces): #recursive function to search for possible moves
        #paths - array of candidate paths
        #currPath - dynamic array that tells where the function is currently searching
        #visitedSpaces - list of (f, g) locations that have already been visited, to avoid infinite loops

        currLoc = currPath[-1] #most recent entry on path, in world coords
        visitedSpaces.append(currLoc) #register current position to avoid infinite loops
        if len(currPath) > 1: #if a valid path, not just start position
            paths.append([x for x in currPath]) #register as valid path (copy array for mutability problem fix)
        for u in self.unitmoves: #check for other spaces surrounding
            coord1 = (currLoc[0] + u[0], currLoc[1] + u[1]) #one and two units in this direction
            coord2 = (currLoc[0] + 2*u[0], currLoc[1] + 2*u[1])
            #if can jump in this direction
            if not coord2 in visitedSpaces\
                    and (self.holes[coord2].marble == None if coord2 in self.holes else False)\
                    and (self.holes[coord1].marble != None if coord1 in self.holes else False): #make sure is unvisited by recursion, empty, and has marble in between
                currPath.append(coord2) #tell next iteration current location
                self.branchMoves(paths, currPath, visitedSpaces) #recursive call
                del currPath[-1] #delete last element to keep track

    def cart(self, coord): #trigonometrically convert (f, g) to cartesian coords
        return ((coord[1]-coord[0])*.5, (coord[1]+coord[0])*math.sqrt(3)/2)

    def sqd(self, a, b): #squared distance between tuples a and b
        return (a[0]-b[0])**2 + (a[1]-b[1])**2

#prompt user for input about player count, etc
def getIntInput(prompt, range): #range is list of acceptable int entries
    reply = 0
    valueOk = False #if input was valid
    while not valueOk:
        valueOk = True #assume was valid unless exception thrown
        try:
            reply = int(input(prompt)) #prompt for input
        except:
            valueOk = False #clear flag if not valid
        if not reply in range: #check to see if it is an acceptable number
            valueOk = False
            print 'Must be one of ' + str(range)
    return reply

def playGame():
    #welcome string
    print "Welcome to Chinese Checkers!\n\nThe goal of the game is to move all your marbles to your opponent's triangle. Each turn consists of either:\n  1. a single move in any direction, or\n  2. a series of jumps over adjacent marbles. Once you start jumping, you can continue jumping as many times as you want with that marble, and hit any key to finish your turn.\nTo move, first select a marble to move. Then, choose the hole to move it into."
    #get player and AI count from user
    players = getIntInput("How many players?", range(2, 7, 2)) #2, 4, or 6 players
    cPlayers = getIntInput("How many AIs?", range(0, players+1)) #can be 0 to all AI players
    #create board instance and begin game
    b = Board(players, cPlayers)
    b.hostGame()

#call the main method
playGame()