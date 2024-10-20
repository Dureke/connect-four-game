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

def findEmptyGame(player):
    for game in gameList:
        player1 = game.getPlayer1()
        player2 = game.getPlayer2()
        if player.getID() == player1.getID() and not player2:
            return game
    return None

def join(usernames):
    if len(usernames) > 2:
        raise ValueError("Too many usernames given.")
    host = getPlayer(usernames[0])
    joiner = getPlayer(usernames[1])

    board = findEmptyGame(host)
    if board:
        board.setPlayer2(joiner)
    else:
        raise Exception(f"No open games for host {host}.")
