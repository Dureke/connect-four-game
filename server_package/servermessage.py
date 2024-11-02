
# import sys
# import selectors
# import json
# import io
# import struct
# import game.movehandler as movehandler
# from action import Action

# request_search = {
#     # Could modify this to become a database of users?
#     # Search for existing games?
#     "user": "No existing users yet!",
#     "game": "No existing games yet!"}


# class Message:
#     def __init__(self, selector, sock, addr):
#         self.selector = selector
#         self.sock = sock
#         self.addr = addr
#         self._recv_buffer = b""
#         self._send_buffer = b""
#         self._jsonheader_len = None
#         self.jsonheader = None
#         self.request = None
#         self.response_created = False
#         self.quit = False
#         self.update = False

#     def _set_selector_events_mask(self, mode):
#         """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
#         if mode == "r":
#             events = selectors.EVENT_READ
#         elif mode == "w":
#             events = selectors.EVENT_WRITE
#         elif mode == "rw":
#             events = selectors.EVENT_READ | selectors.EVENT_WRITE
#         else:
#             raise ValueError(f"Invalid events mask mode {repr(mode)}.")
#         self.selector.modify(self.sock, events, data=self)

#     def _read(self):
#         """Retrieves data from client into self._recv_buffer. Raises exception if no data to retrieve."""
#         try:
#             # Should be ready to read
#             data = self.sock.recv(4096)
#         except BlockingIOError:
#             # Resource temporarily unavailable (errno EWOULDBLOCK)
#             pass
#         else:
#             if data:
#                 self._recv_buffer += data
#             else:
#                 raise RuntimeError("Peer closed.")

#     def _write(self):
#         """Sends data within self._send_buffer data to client."""
#         if self._send_buffer:
#             print("sending", repr(self._send_buffer), "to", self.addr)
#             try:
#                 # Should be ready to write
#                 sent = self.sock.send(self._send_buffer)
#             except BlockingIOError:
#                 # Resource temporarily unavailable (errno EWOULDBLOCK)
#                 pass
#             else:
#                 self._send_buffer = self._send_buffer[sent:]
#                 # Close when the buffer is drained. The response has been sent.
#                 # if sent and not self._send_buffer:
#                 self._set_selector_events_mask("rw")

#     def _json_encode(self, obj, encoding):
#         """Translates json data from string to specificed encoding: utf-8."""
#         return json.dumps(obj, ensure_ascii=False).encode(encoding)

#     def _json_decode(self, json_bytes, encoding):
#         """returns a decoded json object from encoding: utf-8."""
#         tiow = io.TextIOWrapper(
#             io.BytesIO(json_bytes), encoding=encoding, newline=""
#         )
#         obj = json.load(tiow)
#         tiow.close()
#         return obj

#     def _create_message(
#         self, *, content_bytes, content_type, content_encoding
#     ):
#         """creates message with appropriate header: Header, lengh of header, and content.
#         Returns the byte encoded content."""
#         jsonheader = {
#             "byteorder": sys.byteorder,
#             "content-type": content_type,
#             "content-encoding": content_encoding,
#             "content-length": len(content_bytes),
#         }
#         jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
#         message_hdr = struct.pack(">H", len(jsonheader_bytes))
#         message = message_hdr + jsonheader_bytes + content_bytes
#         return message

#     def _create_response_json_content(self):
#         """Creates a response based on what request was sent from the client to server.
#         Supported actions for json content include search."""
#         action = self.request.get("action")
#         value = self.request.get("value")

#         action_methods = {
#             Action.SEARCH.value: self._handle_search,
#             Action.LOGIN.value: self._handle_login,
#             Action.START.value: self._handle_start,
#             Action.JOIN.value: self._handle_join,
#             Action.BEGIN.value: self._handle_begin,
#             Action.MOVE.value: self._handle_move,
#             Action.QUIT.value: self._handle_quit,
#             Action.ERROR.value: self._handle_error
#         }
        
#         if action not in action_methods:
#             content = action_methods[Action.ERROR.value](action)
#         else:
#             content = action_methods[action](value)

#         content_encoding = "utf-8"
#         response = {
#             "content_bytes": self._json_encode(content, content_encoding),
#             "content_type": "text/json",
#             "content_encoding": content_encoding,
#         }
#         return response
    
#     def _handle_error(self, input):
#         return {"error": f"Invalid input \"{input}\"."}
    
#     def _handle_search(self, value):
#         result = request_search.get(value, f'No match for "{value}".')
#         return {"result": result}

#     def _handle_login(self, username):
#         movehandler.login(username, self.sock)
#         return {"result": f"Successfully logged in user {username}."}

#     def _handle_start(self, username):
#         movehandler.startGame(username)
#         return {"result": f"Started game for user {username}."}

#     def _handle_join(self, value):
#         games = movehandler.getAwaitingGames()
#         if not games:
#             return {"join": "No games available."}
#         return {"join": movehandler.gamesToUsername(games)}

#     def _handle_begin(self, value):
#         usernames = value.split(',')
#         movehandler.join(usernames)
#         return {"result": f"User {usernames[1]} joined user {usernames[0]}'s game."}

#     def _handle_move(self, value):
#         username = movehandler.queueMove(value)
#         return {"result": f"User {username} queued a move."}

#     def _handle_quit(self, _):
#         self.quit = True
#         return {"result": "Connection closing. Goodbye!"}

#     def _create_response_binary_content(self):
#         """"""
#         response = {
#             "content_bytes": b"First 10 bytes of request: "
#             + self.request[:10],
#             "content_type": "binary/custom-server-binary-type",
#             "content_encoding": "binary",
#         }
#         return response

#     def process_events(self, mask):
#         if mask & selectors.EVENT_READ:
#             self.read()
#         if mask & selectors.EVENT_WRITE:
#             self.write()
        
#         if not self._recv_buffer and not self._send_buffer and self.quit:
#             self.close()

#     def read(self):
#         self._read()

#         if self._jsonheader_len is None:
#             self.process_protoheader()

#         if self._jsonheader_len is not None:
#             if self.jsonheader is None:
#                 self.process_jsonheader()

#         if self.jsonheader:
#             if self.request is None:
#                 self.process_request()

#     def write(self):
#         if self.request:
#             if not self.response_created:
#                 self.create_response()

#         self._write()
#         self.request = None
#         self._jsonheader_len = None
#         self.jsonheader = None
#         self.response_created = False

#     def close(self):
#         print("closing connection to", self.addr)
#         try:
#             self.selector.unregister(self.sock)
#         except Exception as e:
#             print(
#                 f"error: selector.unregister() exception for",
#                 f"{self.addr}: {repr(e)}",
#             )

#         try:
#             self.sock.close()
#         except OSError as e:
#             print(
#                 f"error: socket.close() exception for",
#                 f"{self.addr}: {repr(e)}",
#             )
#         finally:
#             # Delete reference to socket object for garbage collection
#             self.sock = None

#     def process_protoheader(self):
#         hdrlen = 2
#         if len(self._recv_buffer) >= hdrlen:
#             self._jsonheader_len = struct.unpack(
#                 ">H", self._recv_buffer[:hdrlen]
#             )[0]
#             self._recv_buffer = self._recv_buffer[hdrlen:]

#     def process_jsonheader(self):
#         hdrlen = self._jsonheader_len
#         if len(self._recv_buffer) >= hdrlen:
#             self.jsonheader = self._json_decode(
#                 self._recv_buffer[:hdrlen], "utf-8"
#             )
#             self._recv_buffer = self._recv_buffer[hdrlen:]
#             for reqhdr in (
#                 "byteorder",
#                 "content-length",
#                 "content-type",
#                 "content-encoding",
#             ):
#                 if reqhdr not in self.jsonheader:
#                     raise ValueError(f'Missing required header "{reqhdr}".')

#     def process_request(self):
#         content_len = self.jsonheader["content-length"]
#         if not len(self._recv_buffer) >= content_len:
#             return
#         data = self._recv_buffer[:content_len]
#         self._recv_buffer = self._recv_buffer[content_len:]
#         if self.jsonheader["content-type"] == "text/json":
#             encoding = self.jsonheader["content-encoding"]
#             self.request = self._json_decode(data, encoding)
#             print("received request", repr(self.request), "from", self.addr)
#         else:
#             # Binary or unknown content-type
#             self.request = data
#             print(
#                 f'received {self.jsonheader["content-type"]} request from',
#                 self.addr,
#             )
#         # Set selector to listen for write events, we're done reading.
#         self._set_selector_events_mask("w")

#     def create_response(self):
#         if self.jsonheader["content-type"] == "text/json":
#             response = self._create_response_json_content()
#         else:
#             # Binary or unknown content-type
#             response = self._create_response_binary_content()
#         message = self._create_message(**response)
#         self.response_created = True
#         self._send_buffer += message
