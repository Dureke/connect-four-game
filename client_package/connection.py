import selectors
import logging
import numpy
from client_package.message import Message
from client_package.state import State
from game.action import Action
from game.boards import Board
from game.piece import Piece
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
        if mask & selectors.EVENT_WRITE:
            self.write()
        
        if self.state == State.QUIT:
            self.close()         

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
            self.board = Board(move[0], move[1], int(move[2]))
        else: # update existing board!
            piece = Piece(int(move[1]), int(move[2]), int(move[3]), self.board)
            self.board.setPiece(self.board, piece)

        # move contains username,color,x,y,boardID
        if self.state == State.PLAYER_TURN:
            legal_move = int(self.make_move())
            translate_move = f"{self.username},{self.board.getNextPlayer().value},{legal_move},{self.board.y_index(legal_move)},{self.board.getID()}"
            self.message = Message(self._recv_buffer, self.sock, self.addr, self.username, action=State.PLAYER_TURN.value, value=translate_move)
        else:
            print("\n\n\n\n\n\n", self.board)
            print("Opponents turn.")      
    
    def make_move(self):
        print("\n\n\n\n\n\n", self.board)
        print("Your turn! Select a column to put your piece!")
        move = input()
        if self.board.moveAllowed(self.board, move):
            return move
        else:
            print("Move was not valid.")
            return self.make_move()