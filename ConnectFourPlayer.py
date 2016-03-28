import random
from ConnectFour import Board

class basicPlayer():
    """a basic player class that selects the next move"""
    def __init__(self, ox):
        """the constructor"""
        if(ox != 'X' and ox != 'O'):
            ox = 'X'
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
        return 'O' if self.ox=='X' else 'X'

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
                               scores[colOpp] = 0
                           b.delMove(colOpp)
                b.delMove(col)
            else:
                scores[col] = -1

        return scores

    def nextMove(self, b):
        scores = self.scoresFor(b)
        candidates = [x for x in range(len(scores)) if scores[x]==max(scores)]
        return candidates[random.randrange(len(candidates))]

p = smartPlayer('O')
print p.oppCh()