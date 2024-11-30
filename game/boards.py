from game.piece import Piece
from game.rules import Rules
from game.status import Status
import numpy
import logging

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

    def __init__(self, player1, player2=None, id=count):
        super().__init__()
        self.ID = id
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
        print(f"comparing {self.currentTurn} to {self.player1}")
        if self.currentTurn == self.player1:
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
    
    def y_index(self, x_value):
        deepest_free_space = 99
        for index, value in enumerate(self.board[x_value]):
            if value == 0:
                deepest_free_space = index
        return deepest_free_space
            
    
    def setPiece(self, board, piece):
        x, y = piece.getLocation()
        if not self.moveAllowed(board, x):
            raise RuntimeError("Illegal Move.")
        self.board[x][y] = piece
        self.swap_turns()

        if self.currentTurn == self.player1:
            player = 'a'
        else:
            player = 'b'
    
        self.moveHistory += f"{player}{x}{y},"
        

    def moveAllowed(self, board, move):
        all_legal_columns = [0, 1, 2, 3, 4, 5, 6]
        int_move = int(move)
        if int_move in all_legal_columns:
            piece = Piece(board.getNextPlayer().value, int_move, board.y_index(int_move), board)
            logging.debug(f"Checking locations: {self.locationFree(self.board, piece)}")
            logging.debug(f"Checking turn order: {self.turnOrder(piece)}")
            return self.locationFree(self.board, piece) and self.turnOrder(piece)
        logging.debug(f"Move {int_move} not within available columns {all_legal_columns}.")
        return False
    
    def __str__(self):
        return numpy.array2string(self.board)

