import random
from ConnectFour import Board
import sys

class basicPlayer():
    """a basic player class that selects the next move"""
    def __init__(self, ox):
        """the constructor"""
        if abs(ox) != 1:
            ox = 1
        self.ox = ox

    def __repr__( self ):
        """ creates an appropriate string """
        s = "Basic player for " + self.ox + "\n"
        return s

    def nextMove(self,b):
        """selects an allowable next move at random"""
        col = -1
        while b.allowsMove(col) == False:
            col = random.randrange(b.width)
        return col

class smartPlayer(basicPlayer):
    """ an AI player for Connect Four """
    def __init__(self, ox):
        """ the constructor inherits from from the basicPlayer class"""
        basicPlayer.__init__(self, ox)

    def __repr__( self ):
        """ creates an appropriate string """
        s = "Smart player for " + self.ox + "\n"
        return s

    def oppCh(self):
        return -self.ox

    def scoresFor(self, b):
        scores = [50] * b.width
        for col in range(b.width):
            if b.allowsMove(col):
                b.addMove(col, self.ox)
                if b.winsFor(self.ox):
                    scores[col] = 100
                else:
                   for colOpp in range(b.width):
                       if b.allowsMove(colOpp):
                           b.addMove(colOpp, self.oppCh())
                           if b.winsFor(self.oppCh()):
                               scores[col] = 0
                           b.delMove(colOpp)
                b.delMove(col)
            else:
                scores[col] = -1

        return scores

    def nextMove(self, b):
        scores = self.scoresFor(b)
        print scores
        candidates = [x for x in range(len(scores)) if scores[x]==max(scores)]
        return candidates[random.randrange(len(candidates))]

def playGame(playerX, playerO):

    if playerX == 'smart':
        pX = smartPlayer(1)
    elif playerX == 'basic':
        pX = basicPlayer(1)
    elif playerX != 'human':
        print "Player X should be 'smart', 'basic', or 'human'. Try again!"
        sys.exit()

    if playerO == 'smart':
        pO = smartPlayer(-1)
    elif playerO == 'basic':
        pO = basicPlayer(-1)
    elif playerO != 'human':
        print "Player O should be 'smart', 'basic', or 'human'. Try again!"
        sys.exit()

    b = Board(7, 6)
    print b

    turn = 1
    while not (b.winsFor(1) or b.winsFor(-1) or b.isFull()):
        usercol = -1
        while True:
            usercol = input(("X" if turn==1 else "O") + ", Choose a column: ")\
                if (playerX if turn==1 else playerO)=='human' else (pX if turn==1 else pO).nextMove(b)
            if usercol < 0 or usercol >= b.width or not b.allowsMove(usercol): continue
            break
        b.addMove(usercol, turn)
        print b
        turn *= -1
    if b.isFull():
        print "Truce!"
        sys.exit()
    print ("O" if turn==1 else "X") + " wins!"

playGame("human", "smart")