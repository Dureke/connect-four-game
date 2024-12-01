from game.colors import Color

class Piece():
    count = 0

    def __init__(self, color, x, y, board):
        self.color = color
        self.x = x
        self.y = y 
        self.ID = self.count
        self.count += 1
        self.board = board

    def setLocation(self, x, y):
        self.x = x
        self.y = y
    
    def getLocation(self):
        return self.x, self.y
    
    def getInfo(self):
        return f"Piece [{self.count}]: Color: {self.color}, Location: ({self.x}, {self.y})"
    
    def getBoard(self):
        return self.board
    
    def getColor(self):
        return self.color

    def __str__(self):
        if self.color == Color.RED:
            return "x"
        elif self.color == Color.BLACK:
            return "o"
        else:
            return ""
