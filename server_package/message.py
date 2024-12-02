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
    def __init__(self, buffer, sock, addr, message=None):
        self.buffer = buffer
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response = b""
        self.server_task = ""
        self.sock = sock
        self.addr = addr

        if message:
            action, value = message
            self.request = self._handle_helper(action, value)
        else:
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
        action = self.request["content"]["action"]
        value = self.request["content"]["value"]

        action_methods = {
            Action.SEARCH.value: self._handle_search,
            Action.LOGIN.value: self._handle_login,
            Action.START.value: self._handle_start,
            Action.JOIN.value: self._handle_join,
            Action.BEGIN.value: self._handle_begin,
            Action.MOVE.value: self._handle_move,
            Action.QUIT.value: self._handle_quit,
            Action.BOARD.value: self._handle_board,
            Action.ERROR.value: self._handle_error,
            5: self._handle_player_turn,
            6: self._handle_player_waiting,
            "move_server": self._handle_server_move,
            "end": self._handle_end
        }
        
        if action not in action_methods:
            content = action_methods[Action.ERROR.value](action)
        else:
            content = action_methods[action](value)

        return content
    
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
        response = self._create_response_json_content()
        req = {
            "content_bytes": self._json_encode(response, "utf-8"),
            "content_type": "text/json",
            "content_encoding": "utf-8",
        }
        message = self._create_message(**req)
        if response:
            self.response += message
    
    # def server_message(self):
    #     logging.info(f"Server is sending out messages to user.")

    def _handle_helper(self, action, value):
        return dict(content=dict(action=action, value=value))
    
    def _handle_error(self, input):
        return self._handle_helper("error",f"Invalid input.")
    
    def _handle_search(self, value):
        result = request_search.get(value, f'No match for "{value}".')
        return {"result": result}
    
    def _handle_establish(self, value):
        return self._handle_helper(99, None)

    def _handle_login(self, username):
        logging.debug(f"Registering user with username {username}")
        movehandler.login(username, self.sock)
        self.server_task = f"login:{username}"
        return self._handle_helper("login", username)

    def _handle_start(self, username):
        movehandler.startGame(username)
        return self._handle_helper("start", f"Started game for user {username}.")

    def _handle_join(self, value):
        games = movehandler.getAwaitingGames()
        if not games: 
            return self._handle_helper("join", None)
        return self._handle_helper("join", movehandler.gamesToUsername(games))

    def _handle_begin(self, value): 
        if value[:7] != "waiting":
            usernames = value.split(',')
            movehandler.join(usernames)

            # Server now needs to send a message to both clients that the game shall begin
            self.server_task = f"begin:{usernames[0],usernames[1]}"

            return self._handle_helper("begin", f"User {usernames[1]} joined user {usernames[0]}'s game.")
        else:
            username = value.split(',')[1]
            logging.info(f"Checking to see if player2 joined: {movehandler.has_player2_joined(username)}")
            if movehandler.has_player2_joined(username):
                board_ID = movehandler.has_player2_joined(username)
                logging.info(f"Retrieving player1 from game {board_ID}")
                game = movehandler.findGame(board_ID)
                player1 = game.getPlayer1().getUsername()
                player2 = game.getPlayer2().getUsername()
                return self._handle_helper("move", f"{player1},{player2},{board_ID}")
            # check if anyone joined, if so start game
            return {"begin": "waiting"}

    def _handle_move(self, value):
        # username,color,x,y,boardID
        logging.debug(f"Finding game with ID: {value.split(',')[4]}")
        game = movehandler.findGame(int(value.split(',')[4]))
        player1 = game.getPlayer1().getUsername()
        player2 = game.getPlayer2().getUsername()
        movehandler.queueMove(value)
        win_check = movehandler.is_win(value.split(",")[4])
        if win_check:
            self.server_task = f"end/{player1}/{player2}/{win_check}"
            return None
        self.server_task = f"move/{player1}/{player2}/{value}"
        return None
        
    def _handle_board(self, value):
        board = movehandler.findGame(int(value))
        return {"board": f"{board.getHistory()}"}

    def _handle_quit(self, value):
        self.quit = True
        self.server_task = Action.QUIT.value
        if value == "abort":
            return None
        return self._handle_helper("quit", "Connection closing. Goodbye!")
    
    def _handle_server_move(self, value):
        return self._handle_helper("move", value)

    def _handle_player_turn(self, value):
        return {"break me!", "Oops"}
    
    def _handle_player_waiting(self, value):
        return {"break me!", "you're waiting? oops again"}
    
    def _handle_end(self, value):
        return self._handle_helper("end", value)