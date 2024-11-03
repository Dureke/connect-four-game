import selectors
import logging
from server_package.message import Message
from game.action import Action

class Connection:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self.quit = False
        self.message = None
        self.task = []
        self.username = None
    
    def get_username(self):
        return self.username
    
    def get_address(self):
        return self.addr
    
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
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()
        
        if not self._recv_buffer and not self._send_buffer and self.quit:
            self.close()         

    def read(self):
        """Retrieves data from client into self._recv_buffer. Raises exception if no data to retrieve."""
        try:
            data = self.sock.recv(4096) 
            self._recv_buffer += data
            if not data:
                raise RuntimeError("Peer closed.")
        except BlockingIOError: # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass  
        
        # Create a message with the buffer, and re-obtain the updated buffer
        self.message = Message(self._recv_buffer, self.sock, self.addr)
        self._recv_buffer = self.message.get_remaining_buffer()

        # Get the task and pass it later as a global server action
        server_task = self.message.get_server_task()
        if server_task == Action.QUIT.value:
            self.quit = True
            self._set_selector_events_mask("w")
        elif "login" in server_task:
            self.username = server_task[5:]
        else:
            self.task.append(server_task)
        
        # if _recv_buffer, then create a Server Message
        # store the server message! write can do the below tasks
        # message will return the server task. Offload that task to server
        # message will also create a response, store this response into _send_buffer

    def write(self):
        """Sends data within self._send_buffer data to client."""
        if self.message != None:
            logging.debug(f"added {self.message.get_response()}")
            self._send_buffer += self.message.get_response()
            self.message = None # We're done with this message, discard it

        if self._send_buffer:
            logging.info(f"sending {repr(self._send_buffer)} to {self.addr}")
            try:
                sent = self.sock.send(self._send_buffer)
                self._send_buffer = self._send_buffer[sent:]
                self._set_selector_events_mask("rw")
            except BlockingIOError: # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass

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

    def server_update(self):
        """
        Called by the server, sends local commands that require global server actions.
        Returns an array of all built-up actions, before clearing buffered tasks
        """
        server_task = []
        server_task.copy(self.task)
        self.task = []
        return server_task