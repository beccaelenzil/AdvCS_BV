# python 2
#
# Problem Set 2, Problem 1
# Name:
#

class Board:
    """ a datatype representing a C4 board
        with an arbitrary number of rows and cols
    """

    #Uses 1 and -1 instead of 'O' and 'X'
    def __init__( self, width, height ):
        """ the constructor for objects of type Board """
        self.width = width
        self.height = height
        W = self.width
        H = self.height
        self.data = [ [0]*W for row in range(H) ]

        # we do not need to return inside a constructor!


    def __repr__(self):
        """ this method returns a string representation
            for an object of type Board
        """

        H = self.height
        W = self.width
        s = ''   # the string to return
        for row in range(0,H):
            s += '|'
            for col in range(0,W):
                s += str(self.data[row][col]) + '|'
            s += '\n'

        s += (2*W+1) * '-' + '\n '   # bottom of the board

        for i in range(W):
            s += str(i%10) + " "

        return s       # the board is complete, return it

    def topRow(self, col):
        return self.height - 1 - sum(abs(x) for x in [self.data[row][col] for row in range(self.height)])

    def addMove(self, col, ox):
        row = self.topRow(col)
        if row < self.height:
            self.data[row][col] = ox
            return True
        return False

    def allowsMove(self, col):
        return self.data[0][col] == 0

    def clear(self):
        self.data = [ [0]*self.width for row in range(self.height) ]

    def setBoard( self, moveString ):
        """ takes in a string of columns and places
            alternating checkers in those columns,
            starting with 'X'

            For example, call b.setBoard('012345')
            to see 'X's and 'O's alternate on the
            bottom row, or b.setBoard('000000') to
            see them alternate in the left column.

            moveString must be a string of integers
        """
        nextCh = 1   # start by playing 'X'
        for colString in moveString:
            col = int(colString)
            if 0 <= col <= self.width:
                self.addMove(col, nextCh)
            if nextCh == 1: nextCh = -1
            else: nextCh = 1

    def isFull(self):
        return sum(abs(x) for x in self.data[0]) == self.width

    def delMove(self, col):
        self.data[self.topRow(col) + 1][col] = 0

    def winsFor(self, ox):
        #horiz
        for row in self.data:
            for selection in [row[col:col+4] for col in range(0, self.width-3)]:
                if abs(sum(selection)) == 4:
                    return selection[0] == ox
        #vert
        for col in [[self.data[i][j] for i in range(self.height)] for j in range(self.width)]:
            for selection in [col[idx:idx+4] for idx in range(0, self.height-3)]:
                if abs(sum(selection)) == 4:
                    return selection[0] == ox
        #diag
        for chunk in [[self.data[x/(self.width-3)+k][x%(self.width-3)+k]\
                       for k in range(4)] for x in range((self.width-3)*(self.height-3))]:
            if abs(sum(chunk)) == 4:
                return chunk[0] == ox

        for chunk in [[self.data[self.height-1-(x/(self.width-3))-k][x%(self.width-3)+k]\
                       for k in range(4)] for x in range((self.width-3)*(self.height-3))]:
            if abs(sum(chunk)) == 4:
                return chunk[0] == ox

        return False

c = Board(7, 6)
c.addMove(0, 1)
c.addMove(1, -1)
c.addMove(1, 1)
c.addMove(2, -1)
c.addMove(2, -1)
c.addMove(2, 1)
c.addMove(3, -1)
c.addMove(3, -1)
c.addMove(3, -1)
c.addMove(3, 1)
print c
print c.winsFor(1)