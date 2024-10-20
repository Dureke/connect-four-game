import color

class Rules:

    def __init__(self):
        self.nextPlayer = color.RED

    def cycleTurn(self):
        if self.nextPlayer is color.RED:
            self.setNextPlayer(color.BLACK)
        else:
            self.setNextPlayer(color.RED)

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
