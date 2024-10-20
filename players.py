class Player:

    count = 0

    def __init__(self, username):
        self.username = username
        self.ID = self.count
        self.count += 1

    def getUsername(self):
        return self.username
    
    def getID(self):
        return self.ID
