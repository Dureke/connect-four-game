class Player:

    count = 0

    def __init__(self, username, socket):
        self.username = username
        self.ID = self.count
        self.count += 1
        self.socket = socket

    def getUsername(self):
        return self.username
    
    def getID(self):
        return self.ID

    def getSocket(self):
        return self.socket
    
    def setSocket(self, socket):
        self.socket = socket