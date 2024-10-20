import move

playerList = []
gameList = []
queuedMoves = [] # piece opject

def handle_moves():
    while queuedMoves:
        piece = queuedMoves.pop()
        board = piece.getBoard()

        gameList[board].setPiece(piece)