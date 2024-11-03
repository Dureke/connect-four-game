import json
import io
import struct
import sys
import logging

import game.movehandler as movehandler
from game.action import Action

request_search = {
    "user": "No existing users yet!",
    "game": "No existing games yet!"}

class Message():
    """
    Takes a buffer, and returns the updated buffer, as well as the global
    tasks needed from the message, and the packaged response.
    """
    def __init__(self, buffer, sock, addr):
        self.buffer = buffer
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        self.response = b""
        self.server_task = None
        self.sock = sock
        self.addr = addr

        self.process_requests()
        self.create_response()

    def get_response(self):
        return self.response

    def get_server_task(self):
        return self.server_task
    
    def get_remaining_buffer(self):
        return self.buffer

    def process_requests(self):
        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def _json_encode(self, obj, encoding):
            """Translates json data from string to specificed encoding: utf-8."""
            return json.dumps(obj, ensure_ascii=False).encode(encoding)
    
    def _json_decode(self, json_bytes, encoding):
        """returns a decoded json object from encoding: utf-8."""
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj
    
    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        """creates message with appropriate header: Header, lengh of header, and content.
        Returns the byte encoded content."""
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
    
    def _create_response_json_content(self):
        """Creates a response based on what request was sent from the client to server.
        Supported actions for json content include search."""
        action = self.request.get("action")
        value = self.request.get("value")

        action_methods = {
            Action.SEARCH.value: self._handle_search,
            Action.LOGIN.value: self._handle_login,
            Action.START.value: self._handle_start,
            Action.JOIN.value: self._handle_join,
            Action.BEGIN.value: self._handle_begin,
            Action.MOVE.value: self._handle_move,
            Action.QUIT.value: self._handle_quit,
            Action.ERROR.value: self._handle_error
        }
        
        if action not in action_methods:
            content = action_methods[Action.ERROR.value](action)
        else:
            content = action_methods[action](value)

        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response
    
    def _create_response_binary_content(self):
        """"""
        response = {
            "content_bytes": b"First 10 bytes of request: "
            + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response
    
    def process_protoheader(self):
        logging.debug("Creating protoheader for message.")
        hdrlen = 2
        if len(self.buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self.buffer[:hdrlen]
            )[0]
            self.buffer = self.buffer[hdrlen:]

    def process_jsonheader(self):
        logging.debug("Creating json header for message.")
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

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self.buffer) >= content_len:
            return
        data = self.buffer[:content_len]
        self.buffer = self.buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            logging.info(f"received request {repr(self.request)} from {self.addr}")
        else:
            # Binary or unknown content-type
            self.request = data
            logging.info(f'received {self.jsonheader["content-type"]} request from {self.addr}')

    def create_response(self):
        logging.debug("Assembling a response.")
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            # Binary or unknown content-type
            response = self._create_response_binary_content()
        message = self._create_message(**response)
        self.response_created = True
        self.response += message
    
    def _handle_error(self, input):
        return {"error": f"Invalid input \"{input}\"."}
    
    def _handle_search(self, value):
        result = request_search.get(value, f'No match for "{value}".')
        return {"result": result}

    def _handle_login(self, username):
        movehandler.login(username, self.sock)
        return {"result": f"Successfully logged in user {username}."}

    def _handle_start(self, username):
        movehandler.startGame(username)
        return {"result": f"Started game for user {username}."}

    def _handle_join(self, value):
        games = movehandler.getAwaitingGames()
        if not games:
            return {"join": "No games available."}
        return {"join": movehandler.gamesToUsername(games)}

    def _handle_begin(self, value):
        usernames = value.split(',')
        movehandler.join(usernames)
        return {"result": f"User {usernames[1]} joined user {usernames[0]}'s game."}

    def _handle_move(self, value):
        username = movehandler.queueMove(value)
        return {"result": f"User {username} queued a move."}

    def _handle_quit(self, _):
        self.quit = True
        return {"result": "Connection closing. Goodbye!"}