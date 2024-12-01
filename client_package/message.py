
import sys
import selectors
import json
import io
import struct
import logging
import time
import numpy
from game.status import Status
from game.boards import Board
from game.action import Action
from game.colors import Color

from client_package.state import State

class Message:
    def __init__(self, buffer, sock, addr, username, action=None, value=None):
        self.buffer = buffer
        self.sock = sock
        self.addr = addr
        self.client_task = ""
        self._jsonheader_len = None
        self.jsonheader = None  
        self.server_response = None
        self.client_request = b""
        self.state = State.ESTABLISH
        self.username = username

        if action:
            self.server_response = self._helper_response(action, value)
            logging.info(f"Client queuing message: {self.server_response}")
        else:
            self.process_requests() # translate buffer -> server_response -> client_request
        if self.server_response:
            self.queue_request() # queue client response to server response     
    
    def create_response(self, action, value):
        """For a given action, value pair, send client's response to that to progress state"""
        logging.info(f"creating response for action {action} and value {value}.")
        action_methods = {
            State.ESTABLISH.value: self._establish_response,
            Action.LOGIN.value: self._login_response,
            Action.START.value: self._start_response,
            Action.JOIN.value: self._join_response,
            Action.BEGIN.value: self._begin_response,
            Action.QUIT.value: self._quit_response,
            Action.ERROR.value: self._error_response,
            Action.MOVE.value: self._move_response,
            State.PLAYER_TURN.value: self._make_move_response
        } 
        return action_methods[action](value)

    def queue_request(self):
        content = self.create_response(self.server_response["content"]["action"],self.server_response["content"]["value"])
        content_type = "text/json"
        content_encoding = "utf-8"
        req = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": content_type,
            "content_encoding": content_encoding,
        }
        message = self._create_message(**req)
        if content: # if a response was created in the first place
            self.client_request += message
    
    def get_state(self):
            return self.state
    
    def _helper_response(self, action, value):
        return dict(content=dict(action=action, value=value))
    
    def _establish_response(self, value):
        self.state = State.LOGIN
        return self._helper_response("login", self.username)

    def _login_response(self, value): # sucessful login, get input
        self.state = State.CLIENT_INPUT

        return self._helper_response(self.get_input(["start", "join", "quit"]), self.username)
    
    def get_input(self, possible_actions):
        player_action = None
        while not player_action:
            print(f"\n\nPlease select an action to take!\n"
                  + f"Possible actions: {possible_actions}")
            player_action = input()
            if player_action in possible_actions:
                return player_action
            else:
                print(f"{player_action} is not a possible action.")
                player_action = ""
    
    def _start_response(self, value): # server sucessfully started, waiting on player
        self.state = State.START_WAITING
        return None # we will wait for the server to let us know if someone joins
    
    def _join_response(self, value):
        # value contains all possible users to join, if empty, no one to join
        logging.debug(f"Got join response of {value}")
        if value: # there are users to join
            return self._helper_response("begin", f"{self.get_input(value)},{self.username}")
        else: 
            return self._login_response(self.username)
        
    def _begin_response(self, value):
        self.state = State.JOIN_WAITING
        return None
        
    def _quit_response(self, value):
        self.state = State.QUIT
        logging.info(f"Server responded with message: {value}")
        return None # server already closed connection, don't send a message back

    def _error_response(self, value):
        self.state = State.QUIT
        return None 
    
    def _move_response(self, value):
        move_split = value.split(',')
        move_username = move_split[0].replace('\'', "")
        if move_username == self.username:
            self.state = State.PLAYER_WAITING
            return None
        else:
            self.state = State.PLAYER_TURN
            return None
    
    def _make_move_response(self, value):
        return self._helper_response("move", value)
        
    def get_move(self):
        if self.server_response["content"]["action"] == "move":
            move = self.server_response["content"]["value"]
            logging.info(f"Retrieving move {move.split(',')}")
            return move.split(",")
        return None

























    def process_requests(self):
        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.server_response is None:
                self.process_response()
        

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

    def process_protoheader(self):
        hdrlen = 2
        if len(self.buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self.buffer[:hdrlen]
            )[0]
            self.buffer = self.buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self.buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self.buffer[:hdrlen], "utf-8"
            )
            self.buffer = self.buffer[hdrlen:]
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
        if not len(self.buffer) >= content_len:
            return
        data = self.buffer[:content_len]
        self.buffer = self.buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.server_response = self._json_decode(data, encoding)
            logging.info(f"received response {repr(self.server_response)} from {self.addr}")

    def get_remaining_buffer(self):
        return self.buffer
    
    def get_response(self):
        return self.client_request
