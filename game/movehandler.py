import game.piece as piece
import game.players as players
import game.boards as boards
from game.colors import Color
import logging

playerList = []
gameList = []
queuedMoves = [] # piece opject
queuedUpdate = []


def getAwaitingGames():

    awaitingGames = []
    for game in gameList:
        if not game.getPlayer2():
            awaitingGames.append(game)

    logging.info(f"Retrieved {awaitingGames.__len__()} free games.")
    return awaitingGames

def gamesToUsername(games):
    usernames = []
    for game in games:
        logging.info(f"Current game Player 1: {game.getPlayer1()}, Player 2: {game.getPlayer2()}")
        usernames.append(game.getPlayer1().getUsername())
    logging.info(f"Translating game into {usernames}")
    return usernames

def handle_moves():
    while queuedMoves:
        piece = queuedMoves.pop()
        board = piece.getBoard()

        for game in gameList:
            if game == board:
                game.setPiece(board, piece)

def getPlayer(username):
    for player in playerList:
        if player.getUsername() == username:
            return player
    return None

def addPlayer(username, socket):
    playerList.append(players.Player(username, socket))

def removePlayer(player):
    playerList.remove(player)

def addGame(player1, player2):
    gameList.append(boards.Board(player1, player2))

def removeGame(board):
    gameList.remove(board)

def login(username, socket):
    if not getPlayer(username): # no player of that username, register new player
        addPlayer(username, socket)
    else:
        getPlayer(username).setSocket(socket)

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
    logging.info(f"Searching {gameList}")
    for game in gameList:
        if game.getID() == boardID:
            return game
    return None

def has_player2_joined(username):
    for game in gameList:
        if game.getPlayer1() and game.getPlayer2():
            logging.debug(f"Checking for player with name: {username}")
            logging.debug(f"player1: {game.getPlayer1().getUsername()}, player2: {game.getPlayer2().getUsername()}")
        # Only games that have both player1 and player2
            if game.getPlayer1().getUsername() == username:
                # if this game matches the username searching for their game, return that
                return game.getID()
            elif game.getPlayer2().getUsername() == username:
                return game.getID()
    return None

def findPlayerSocket(socket):
    for game in queuedUpdate:
        if game.getPlayer1().getSocket() == socket:
            return game
        elif game.getPlayer2().getSocket() == socket:
            return game
    return None

def getUpdate(socket):
    update = findPlayerSocket(socket)
    queuedUpdate.remove(update)
    return update

def join(usernames):
    if len(usernames) > 2:
        raise ValueError("Too many usernames given.")
    host = getPlayer(usernames[0])
    joiner = getPlayer(usernames[1])

    board = findEmptyGame(host)
    if board:
        logging.info(f"Found board: game between {host.getUsername()} and {joiner.getUsername()} begins.")
        board.setPlayer2(joiner)
    else:
        raise Exception(f"No open games for host {host}.")

def queueMove(value):
    # username,color,x,y,boardID
    parsed_value = value.split(',')
    logging.debug(f"Queued move: {parsed_value}")
    username = parsed_value[0]
    color = translateColor(parsed_value[1])
    x, y = translateXY(parsed_value[2], parsed_value[3])
    board = translateBoardID(parsed_value[4])

    board.swap_turns()

    queuedMoves.append(piece.Piece(color, x, y, board))
    logging.debug("Move sucessfully queued.")
    return username

def translateColor(string):
    if string == "1":
        return Color.RED.value
    else:
        return Color.BLACK.value
    
def translateXY(stringX, stringY):
    return int(stringX), int(stringY)

def translateBoardID(string):
    board = findGame(int(string))
    if not board:
        raise Exception(f"No existing game of board ID {int(string)} found.")
    else:
        return board