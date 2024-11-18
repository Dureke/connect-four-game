import game.colors as colors

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

    def __str__(self):
        if self.color == colors.RED:
            return "x"
        elif self.color == colors.BLACK:
            return "o"
        else:
            return ""
