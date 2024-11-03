
import sys
import selectors
import json
import io
import struct
import logging
import time
from game.status import Status
from game.boards import Board
from game.action import Action

import client_package.clientstate as clientstate

def fill_request(reqType, reqEncoding, reqAction, reqValue):
    return dict(
        type=reqType,
        encoding=reqEncoding,
        content=dict(action=reqAction, value=reqValue),
    )
def fill_text_request(reqAction, reqValue):
    return fill_request("text/json", "utf-8", reqAction, reqValue)

def create_request(action, value):
    """Creates a protocol for the client request, to be sent to the clientmessage Message."""
    possibleActions = ["search", "login", "start", "join", "move", "quit"]
    if possibleActions.__contains__(action):
        return fill_text_request(action, value)
    
    elif action == "double" or action == "negate":
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content= struct.pack('>6si', bytes(action, encoding="utf-8"), int(value))
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + value, encoding="utf-8"),
        )

class Message:
    def __init__(self, selector, sock, addr, request):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request = request
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None
        self.state = clientstate.State()
        self.quit = False
        self.username = request["content"]["value"]

        self.gameBoard = None
        self.gameStatus = None
        self.isUserTurn = False

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

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            logging.info(f"sending {repr(self._send_buffer)} to {self.addr}")
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _process_response_json_content(self):
        content = self.response
        logging.info(f"Processing contents {content}")
        if content.get("result"):
            result = content.get("result")
            print(f"\n\ngot result: {result}\n\n")
            if result.__contains__("Connection closing"):
                self.quit = True
        elif content.get("join"): # returns list of possible joins
            username = content.get("join")
            self.join_a_username(username)
        elif content.get("begin"):
            value = content["begin"]
            if value == Status.WAITING.value:
                logging.info("Ack: Still waiting...")
            else: # We have a connection!
                self.gameStatus = Status.BEGIN

    def join_a_username(self, result):
        print(f"\n\nPlease join an existing game:\n\n")
        username = self.response['join']
        if username == "No games available.":
            return
        self.state.set_possible_joins(self.response['join'])
        print(self.state.get_possible_joins())

    def _process_response_binary_content(self):
        content = self.response
        logging.info(f"got response: {repr(content)}")

    def create_new_request(self):
        logging.info("Creating a new request...")
        previous_request = self.request["content"]["action"]
        possible_actions = self.state.get_next_states(previous_request)
        next_action = ""
        try:
            while not next_action and not self.quit and not self.gameStatus:
                """while we dont have a valid action and we aren't quitting
                if possible actions are empty, it means we tried to join when theres nothing to join
                if the next action is valid, set it as the action to be taken
                if the previous action was start, they need to wait for someone to join
                send periodic request from server to see if anyone joined
                if previous action was to join, and it was sucessful, they need to 
                begin the game state
                """
                if not possible_actions:
                    possible_actions = self.state.no_join()
                    print("\n\nNo open games available!")
                    self.request["content"]["action"] = "None"
                print(f"\n\nPlease select an action to take!\n"
                      + f"Possible actions: {possible_actions}")
                logging.info(f"Before request contents: {self.request}")
                next_action = input()
                if next_action in possible_actions:
                    self.request["content"]["action"] = next_action
                    if next_action == Action.START.value:
                        self.gameStatus = Status.WAITING
                        self.gameBoard = Board(self.username, next_action)
                        self.request["content"]["value"] = self.username
                        self.queue_request()
                        self._request_queued = True
                        self._set_selector_events_mask("rw")
                    if previous_request == Action.JOIN.value:
                        self.gameStatus = Status.WAITING
                        self.gameBoard = Board(self.username, next_action)
                        username = self.request["content"]["value"]
                        self.request["content"]["value"] = f"{next_action},{self.username}"
                        self.request["content"]["action"] = "begin"
                        self.queue_request()
                        self._request_queued = True
                        self._set_selector_events_mask("rw")
                        
                # elif next_action in self.state.get_possible_joins():
                #     username = self.request["content"]["value"]
                #     self.request["content"]["value"] = f"{self.username},{next_action}"
                #     self.request["content"]["action"] = "begin"
                #     self.queue_request()
                #     self._request_queued = True
                #     self._set_selector_events_mask("rw")
                else:
                    next_action = ""

                logging.info(f"After request contents: {self.request}")        
        except Exception as err:
            logging.exception(f"Exception: Uncaught error.\n{err}")
        if not self.gameStatus:
            self.queue_request()
            self._request_queued = True
            self._set_selector_events_mask("rw")

    def process_events(self, mask):
        logging.info(f"Process events occurring for user {self.username}")

        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()
        
        #create another event read, if theres nothing queued and no response waiting
        if self.gameStatus == Status.WAITING:
            time.sleep(2.5)
            logging.debug("Status waiting, seeing if player has joined lobby...\n\n\n\n\n")
            self.request = fill_text_request("begin", Status.WAITING.value+self.username)
            self.queue_request()
            self._request_queued = True
            self._set_selector_events_mask("rw")
        elif not self.response and not self._request_queued:
            self.create_new_request()
            
        if not self._recv_buffer and self._send_buffer and self.quit:
            self.close()

    def read(self):
        logging.debug("begin reading...")
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.response is None:
                self.process_response()

    def write(self):
        logging.debug("begin writing...")
        if not self._request_queued:
            self.queue_request()

        self._write()

        if self._request_queued:
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
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

    def queue_request(self):
        content = self.request["content"]
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]
        if content_type == "text/json":
            req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        else:
            req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_response(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.response = self._json_decode(data, encoding)
            logging.info(f"received response {repr(self.response)} from {self.addr}")
            self._process_response_json_content()
        else:
            # Binary or unknown content-type
            self.response = data
            logging.info(f'received {self.jsonheader["content-type"]} response from {self.addr}')

            if self.response.__contains__(b"result"):
                logging.info(f"got response: {repr(self.response)}")
                value = struct.unpack(">6si", self.response)[1]
                logging.info(f"result: {value}")
            else:
                self._process_response_binary_content()
        # Close when response has been processed
        self.response = None
        self._jsonheader_len = None
        self.jsonheader = None
        self._request_queued = False
