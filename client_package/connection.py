import selectors
import logging
import numpy
from client_package.message import Message
from client_package.state import State
from game.action import Action
from game.boards import Board
from game.piece import Piece
from game.colors import Color
import time

class Connection:
    def __init__(self, selector, sock, addr, username):
        self.selector = selector
        self.sock = sock
        self.addr = addr

        self._recv_buffer = b""
        self._send_buffer = b""
        self.state = 1 # state is auto set to 1, because we are sending login message
        self.username = username
        self.aborting = False
        self.message = Message(self._recv_buffer, self.sock, self.addr, self.username, action=State.ESTABLISH.value)

        self._send_buffer += self.message.get_response()
        self.message = None
        self.board = numpy.empty((6,7))
    
    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)
    
    def process_events(self, mask):
        logging.debug(f"Current masks: Read {mask & selectors.EVENT_READ}, Write {mask & selectors.EVENT_WRITE}")

        if mask & selectors.EVENT_READ:
            self.read()
        if self.state == State.QUIT:
            self.close()
            return
        if mask & selectors.EVENT_WRITE:
            self.write()
        
               

    def read(self):
        """Retrieves data from client into self._recv_buffer. Raises exception if no data to retrieve."""
        try:
            data = self.sock.recv(4096) 
            self._recv_buffer += data
            if not data:
                raise RuntimeError("Peer closed.")
        except BlockingIOError: # Resource temporarily unavailable (errno EWOULDBLOCK)
            logging.debug("Blocked.")
            pass  
        
        self.parse_buffer()
        

    def write(self):
        if self._send_buffer:
            logging.info(f"sending {repr(self._send_buffer)} to {self.addr}")
            try:
                sent = self.sock.send(self._send_buffer)
                self._send_buffer = self._send_buffer[sent:]
            except BlockingIOError: # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
        self._set_selector_events_mask("r")

    def close(self):
        logging.info(f"closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            logging.exception(f"error: selector.unregister() exception for {self.addr}: {repr(e)}")

        try:
            self.sock.close()
        except OSError as e:
            logging.exception(f"error: socket.close() exception for {self.addr}: {repr(e)}")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def client_update(self):
        """
        Called by the client, sends local commands that require global client actions.
        Returns an array of all built-up actions, before clearing buffered tasks
        Possible actions for the client: board updates, board game start, board game end
        """
        client_task = self.task.copy()
        self.task = []
        return client_task
    
    def parse_buffer(self):
        self.message = Message(self._recv_buffer, self.sock, self.addr, self.username)
        self._recv_buffer = self.message.get_remaining_buffer()
        self.state = self.message.get_state()
        if self.state:
            if self.state == State.PLAYER_TURN or self.state == State.PLAYER_WAITING:
                self.send_move_message()
            if self.state == State.END_GAME_WIN:
                # display end game message
                # reset message back to input
                print("CONGRADULATIONS! You've won your match!")
                time.sleep(3)
                self.message = Message(self._recv_buffer, self.sock, self.addr, self.username, action="login", value=self.username)
                
            if self.state == State.END_GAME_LOSS:
                print("MATCH LOSS! Try again?")
                time.sleep(3)
                self.message = Message(self._recv_buffer, self.sock, self.addr, self.username, action="login", value=self.username)
                
                
            self._set_selector_events_mask("w")
            logging.debug(f"client tasks are: {self.state}")
            logging.debug(f"added {self.message.get_response()} to send buffer.")
            self._send_buffer += self.message.get_response()
        else:
            self._set_selector_events_mask("rw")

    def send_move_message(self):
        # update board!
        move = self.message.get_move()
        if len(move) == 3: # initalizing!
            if move[0] == self.username:
                color = 1
            else:
                color = 2
            self.board = Board(move[0], move[1], int(move[2]), color)
        else: # update existing board!
            piece = Piece(int(move[1]), int(move[2]), int(move[3]), self.board)
            self.board.setPiece(self.board, piece)

        # move contains username,color,x,y,boardID
        color = self.board.getNextPlayer()
        logging.info(f"Ding, got {color} of type {type(color)}")
        if self.state == State.PLAYER_TURN:
            if color == 1:
                piece_char = "\u25CE"
            else:
                piece_char = "\u25C9"
            legal_move = int(self.make_move(piece_char))
            translate_move = f"{self.username},{self.board.getNextPlayer()},{legal_move},{self.board.y_index(legal_move)},{self.board.getID()}"
            self.message = Message(self._recv_buffer, self.sock, self.addr, self.username, action=State.PLAYER_TURN.value, value=translate_move)
        else:
            if color == 1:
                piece_char = "\u25CE"
            else:
                piece_char = "\u25C9"
            print("\n\n\n\n\n\n", self.board)
            print("Opponents turn.")
            print(f"{piece_char}{piece_char}   - Your color -   {piece_char}{piece_char}")
    
    def make_move(self, piece_char):
        print("\n\n\n\n\n\n", self.board)
        print("Your turn! Select a column to put your piece!")
        print(f"{piece_char}{piece_char}   - Your color -   {piece_char}{piece_char}")
        move = input()
        if self.board.moveAllowed(self.board, move):
            return move
        else:
            print("Move was not valid.")
            return self.make_move(piece_char)
        
    def abort(self):
        logging.debug("User quitting prematurely, aborting.")
        self.message = Message(self._recv_buffer, self.sock, self.addr, self.username, action=State.QUIT.value, value="abort")
        self._send_buffer = self.message.get_response()
        while (self._send_buffer):
            try:
                sent = self.sock.send(self._send_buffer)
                self._send_buffer = self._send_buffer[sent:]
            except BlockingIOError: # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
        self.close()
        