import Color

class Piece(Color):
    count = 0

    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y 
        self.ID = self.count
        self.count += 1

    def setLocation(self, x, y):
        self.x = x
        self.y = y
    
    def getLocation(self):
        return self.x, self.y
    
    def getInfo(self):
        return f"Piece [{self.count}]: Color: {self.color}, Location: ({self.x}, {self.y})"
    
    def __str__(self):
        if self.color == Color.RED:
            return "X"
        elif self.color == Color.BLACK:
            return "O"
        else:
            return "_"
