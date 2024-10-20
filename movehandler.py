import move
import players
import boards

playerList = []
gameList = []
queuedMoves = [] # piece opject

def handle_moves():
    while queuedMoves:
        piece = queuedMoves.pop()
        board = piece.getBoard()

        gameList[board].setPiece(piece)

def getPlayer(username):
    for player in playerList:
        if player.getUsername() == username:
            return player
    return None

def addPlayer(username):
    playerList.append(players.Player(username))

def removePlayer(player):
    playerList.remove(player)

def addGame(player1, player2):
    gameList.append(boards.Board(player1, player2))

def removeGame(board):
    gameList.remove(board)

def login(username):
    if not getPlayer(username): # no player of that username, register new player
        addPlayer(username)

def startGame(username):
    player = getPlayer(username)
    addGame(player, None)