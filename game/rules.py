from game.colors import Color
import logging

class Rules:

    def __init__(self):
        self.nextPlayer = Color.RED

    def cycleTurn(self):
        if self.nextPlayer is Color.RED:
            self.setNextPlayer(Color.BLACK)
        else:
            self.setNextPlayer(Color.RED)

    def locationFree(self, board, piece):
        x, y = piece.getLocation()
        logging.info(f"Checking locations [{x}][{y}] for if free: [{board[x][y]}]")
        if board[x][y]:
            return False
        else: # a color piece exists here
            return True

    def turnOrder(self, piece):
        color = piece.getColor()
        logging.debug(f"Comparing next player {self.nextPlayer} and piece color {color}")
        return self.nextPlayer.value == color
    
    def getNextPlayer(self):
        return self.nextPlayer
    
    def setNextPlayer(self, color):
        self.nextPlayer = color
