import piece
import players
import boards
import colors

playerList = []
gameList = []
queuedMoves = [] # piece opject

def getAwaitingGames():

    awaitingGames = []
    for game in gameList:
        print(f"game: {game.getPlayer1()} and {game.getPlayer2()}")
        if not game.getPlayer2():
            awaitingGames.append(game)

    return awaitingGames

def gamesToUsername(games):
    usernames = []
    for game in games:
        usernames.append(game.getPlayer1().getUsername())
    return usernames

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

def findGame(boardID):
    for game in gameList:
        if game.getID == boardID:
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

def queueMove(value):
    # username,color,x,y,boardID
    parsed_value = value.split(',')
    username = parsed_value[0]
    color = translateColor(parsed_value[1])
    x, y = translateXY(parsed_value[2], parsed_value[3])
    board = translateBoardID(parsed_value[4])

    queuedMoves.append(piece.Piece(color, x, y, board))
    return username

def translateColor(string):
    if string == "red":
        return colors.RED
    else:
        return colors.BLACK
    
def translateXY(stringX, stringY):
    return int(stringX), int(stringY)

def translateBoardID(string):
    board = findGame(int(string))
    if not board:
        raise Exception(f"No existing game of board ID {int(string)} found.")
    else:
        return board