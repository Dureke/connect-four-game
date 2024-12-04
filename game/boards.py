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
        logging.debug(f"comparing {self.currentTurn} to {self.player1}")
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
            if type(value[x_value]) == int:
                deepest_free_space = index
        return deepest_free_space
            
    
    def setPiece(self, board, piece):
        x, y = piece.getLocation()
        if not self.moveAllowed(board, x):
            raise RuntimeError("Illegal Move.")
        self.board[y][x] = piece
        self.swap_turns()

        if self.currentTurn == self.player1:
            player = 'a'
        else:
            player = 'b'
    
        self.moveHistory += f"{player}{x}{y},"
        

    def moveAllowed(self, board, move):
        all_legal_columns = [0, 1, 2, 3, 4, 5, 6]
        if move == "":
            return False
        if not move.isdigit():
            return False
        int_move = int(move)
        if int_move in all_legal_columns:
            if board.y_index(int_move) == 99:
                return False
            piece = Piece(board.getNextPlayer(), board.y_index(int_move), int_move, board)
            return self.locationFree(self.board, piece) and self.turnOrder(piece)
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
                    if color == 1:
                        piece_char = "\u25CE"
                    else:
                        piece_char = "\u25C9"
                    row_string += piece_char + " | "
            row_string += "\n |---|---|---|---|---|---|---|\n"
            board_string += row_string
        board_string += "   0   1   2   3   4   5   6   "
        return board_string
                    
    def is_win(self):
        #check horizontal for wins
        #check vertical for wins
        # check left diagnal for wins
        # check right diagnal for wins
        # return color of winner, if any, otherwise return 0

        horizontal = self.check_horizontal()
        vertical = self.check_vertical()
        left_diagnal = self.check_left_diagnal()
        right_diagnal = self.check_right_diagnal()
        if horizontal:
            winning_color = horizontal
        elif vertical:
            winning_color = vertical
        elif left_diagnal:
            winning_color = left_diagnal
        elif right_diagnal:
            winning_color = right_diagnal
        else:
            winning_color = 0
        
        return winning_color

    def check_horizontal(self):
        for row in numpy.array([0, 1, 2, 3, 4, 5]):
            count = 0
            color = 0
            for column in numpy.array([0, 1, 2, 3, 4, 5, 6]):
                is_win, color, count = self.check_helper(self.board[row][column], color, count)
                if is_win:
                    return is_win
        return 0
    
    def check_vertical(self):
        for column in numpy.array([0, 1, 2, 3, 4, 5, 6]):
            count = 0
            color = 0
            for row in numpy.array([0, 1, 2, 3, 4, 5]):
                is_win, color, count = self.check_helper(self.board[row][column], color, count)
                if is_win:
                    return is_win
        return 0
    
    def check_left_diagnal(self):
        # diagnals coming from top left to bottom right    
        for row_diagnal in numpy.array([0, 1, 2]):
            column = 0
            row = row_diagnal
            color = 0
            count = 0
            while (column < 7 and row < 6):
                is_win, color, count = self.check_helper(self.board[row][column], color, count)
                if is_win:
                    return is_win
                column += 1
                row += 1
        
        for column_diagnal in numpy.array([1, 2, 3]):
            column = column_diagnal
            row = 0
            color = 0
            count = 0
            while (column < 7 and row < 6):
                is_win, color, count = self.check_helper(self.board[row][column], color, count)
                if is_win:
                    return is_win
                column += 1
                row += 1

        return 0
    
    def check_right_diagnal(self):
        # diagnals coming from top right to bottom left
        for row_diagnal in numpy.array([3, 4, 5]):
            column = 0
            row = row_diagnal
            color = 0
            count = 0
            while (column < 7 and row > -1):
                is_win, color, count = self.check_helper(self.board[row][column], color, count)
                if is_win:
                    return is_win
                column += 1
                row -= 1
        
        for column_diagnal in numpy.array([1, 2, 3]):
            column = column_diagnal
            row = 0
            color = 0
            count = 0
            while (column < 7 and row > -1):
                is_win, color, count = self.check_helper(self.board[row][column], color, count)
                if is_win:
                    return is_win
                column += 1
                row -= 1

        return 0
    
    def check_helper(self, spot, color, count):
        if type(spot) == Piece:
            if count == 0:
                color = spot.getColor()
                count += 1
            elif color == spot.getColor():
                count += 1
                if count >= 4:
                    if color == 1:
                        player = self.getPlayer1().getUsername()
                    else:
                        player = self.getPlayer2().getUsername()
                    return player, color, count
            else:
                count = 1
                color = spot.getColor()
        else:
            color = 0
            count = 0
        return None, color, count