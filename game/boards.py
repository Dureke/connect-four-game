from game.piece import Piece
from game.rules import Rules
from game.status import Status
import numpy

def buildBoard(raw_board):
    processed_board = raw_board.split(',')
    new_board = numpy.empty((6,7))
    for player_action in processed_board:
        if player_action[0] == 'a': # if the command is player 1...
            new_board[player_action[1]][player_action[2]] = 'x'
        else:
            new_board[player_action[1]][player_action[2]] = 'o'
    return new_board

class Board(Rules):

    count = 1

    def __init__(self, player1, player2=None):
        self.ID = self.count
        self.player1 = player1
        self.player2 = player2
        self.board = numpy.zeros((6,7), dtype=object)
        self.count += 1
        self.status = Status.WAITING
        self.currentTurn = self.player1
        self.moveHistory = ""
    
    def getPlayer1(self):
        return self.player1
    
    def getPlayer2(self):
        return self.player2

    def getCurrentPlayerTurn(self):
        return self.currentTurn
    
    def swap_turns(self):
        print(f"comparing {self.currentTurn.getID()} to {self.player1.getID()}")
        if self.currentTurn.getID() == self.player1.getID():
            self.currentTurn = self.player2
        else:
            self.currentTurn = self.player1


    def setPlayer2(self, player):
        self.player2 = player
    
    def getID(self):
        return self.ID
    
    def getBoard(self):
        return self.board
    
    def gameStarted(self):
        return self.player2
    
    def getHistory(self):
        return self.moveHistory
    
    def setPiece(self, piece):
        if not self.moveAllowed(self, piece):
            raise RuntimeError("Illegal Move.")
        x, y = piece.getLocation()
        self.board[x, y] = piece.__str__()
        self.swap_turns(self)

        if self.currentTurn == self.player1:
            player = 'a'
        else:
            player = 'b'
    
        self.moveHistory += f"{player}{x}{y},"
        

    def moveAllowed(self, piece):
        return Rules.locationFree(self.board, piece) and Rules.turnOrder(self.nextPlayer, piece)
    
    def __str__(self):
        return numpy.matrix(self.board)

