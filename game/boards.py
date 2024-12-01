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

    def __init__(self, player1, player2=None, id=count,  color=1):
        super().__init__(color)
        self.ID = id
        self.player1 = player1
        self.player2 = player2
        self.board = numpy.array([[0, 1, 2, 3, 4, 5, 6],
                                  [0, 1, 2, 3, 4, 5, 6],
                                  [0, 1, 2, 3, 4, 5, 6],
                                  [0, 1, 2, 3, 4, 5, 6],
                                  [0, 1, 2, 3, 4, 5, 6],
                                  [0, 1, 2, 3, 4, 5, 6]], dtype=object)
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
        for index, value in enumerate(self.board):
            logging.debug(f"Checking {value}...({type(value[x_value])}) Is {value[x_value]} == 0?")
            if type(value[x_value]) == int:
                deepest_free_space = index
        logging.debug(f"Returning {deepest_free_space}")
        return deepest_free_space
            
    
    def setPiece(self, board, piece):
        x, y = piece.getLocation()
        if not self.moveAllowed(board, x):
            raise RuntimeError("Illegal Move.")
        logging.debug(f"DEBUG: {x}, {type(x)} : {y}, {type(y)}")
        self.board[y][x] = piece
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
            if board.y_index(int_move) == 99:
                return False
            piece = Piece(board.getNextPlayer(), board.y_index(int_move), int_move, board)
            logging.debug(f"Checking locations: {self.locationFree(self.board, piece)}")
            logging.debug(f"Checking turn order: {self.turnOrder(piece)}")
            return self.locationFree(self.board, piece) and self.turnOrder(piece)
        logging.debug(f"Move {int_move} not within available columns {all_legal_columns}.")
        return False
    
    def __str__(self):
        board_string = "|---|---|---|---|---|---|---|\n"
        for row in self.board:
            row_string = " | "
            for spot in row:
                if type(spot) == int:
                    row_string += "\u25CC | "
                else:
                    color = spot.getColor()
                    logging.info(f"DEBUG: {color}")
                    if color == 1:
                        piece_char = "\u25CE"
                    else:
                        piece_char = "\u25C9"
                    row_string += piece_char + " | "
            row_string += "\n |---|---|---|---|---|---|---|\n"
            board_string += row_string
        board_string += "   0   1   2   3   4   5   6   "
        return board_string
                    

