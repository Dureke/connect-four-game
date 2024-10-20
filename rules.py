import Color

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
        if board[x, y] is None:
            return True
        else: # a color piece exists here
            return False

    def turnOrder(self, piece):
        color = piece.getColor()
        return self.nextPlayer == color
    
    def getNextPlayer(self):
        return self.nextPlayer
    
    def setNextPlayer(self, color):
        self.nextPlayer = color
