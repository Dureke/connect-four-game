from game.piece import Piece
from game.rules import Rules
from game.status import Status
import numpy

class Board(Rules):

    count = 1

    def __init__(self, player1, player2=None):
        self.ID = self.count
        self.player1 = player1
        self.player2 = player2
        self.board = numpy.empty((6,7))
        self.count += 1
        self.status = Status.WAITING
    
    def getPlayer1(self):
        return self.player1
    
    def getPlayer2(self):
        return self.player2

    def setPlayer2(self, player):
        self.player2 = player
    
    def getID(self):
        return self.ID
    
    def getBoard(self):
        return self.board
    
    def gameStarted(self):
        return self.player2
    
    def setPiece(self, piece):
        if not self.moveAllowed(self, piece):
            raise RuntimeError("Illegal Move.")
        x, y = piece.getLocation()
        self.board[x, y] = piece
        Rules.cycleTurn(self)

    def moveAllowed(self, piece):
        return Rules.locationFree(self.board, piece) and Rules.turnOrder(self.nextPlayer, piece)
    
    def __str__(self):
        return numpy.matrix(self.board)
