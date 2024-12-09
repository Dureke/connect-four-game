# Connect Four Python Game with Sockets

This is a simple Connect Four game implemented using Python and sockets.
**How to run:**
1. **Start the server:** Run the `Server.py` script.
   - To play with default settings, run in a terminal with `python server.py`
   - There is two optional arguments: IP address and Port
     - First optional arg is the server IP address, default value set to 0.0.0.0.
     - Second optional arg is the port number of the server, default value set to 65432.
     - Example: `py Server.py -i 0.0.0.0 -p 65432` is equivalent to `py Server.py -p 65432`.
   - Use `py Server.py -h` for additional information.
     
3. **Start one or more clients:** Run the `Client.py` script.
   - To play with default settings, run in a terminal with `python client.py`
   - There are four optional arguments, IP address, Port, Action, Value
     - First optional arg is the the server IP address, default value set to 127.0.0.1.
     - Second optional arg is the port number of the server the client is connecting to, default value set to 65432.
     - Third optional arg is the command login, default is set to login. There is no other action that can be taken.
     - Forth optional arg is the username that you'd login as, default is set to user#, where # is a random value between 0-1000.
   - Example: `py Client.py -i 127.0.0.1 -p 65432 login username` or `py Client.py -i 127.0.0.1 -p 65432 login testUser`.
   - Use `py Client.py -h` for additional information.
     
5. **Write messages to Server**: In the client terminal, follow the prompts given by the client text application. If there is another game hosted by another client, the join action will work. Otherwise, you can create a game with the start action. Otherwise type quit and disconnect with the quit action, or use a keyboard interrupt to end the client session.

Example Series of Inputs:
- Run `py server.py` in a new terminal.
- Run `py client.py login user1` in a new terminal.
- Run `py client.py login user2` in a new terminal.
- In terminal with user1, type `start`
- In terminal with user2, type `join`
- In terminal with user2, type `user1`
- Follow the prompt until a user wins!

**Rules:** 
* The player who joins is the player to go first
* Each will have the opportunity to drop their color in one of the columns, with only one action per turn
* Tokens can connect 4 diagonally, vertically, and horizontally
* The game board will be 7 spaces wide and 6 spaces tall

**Reference:**
* The rules will be based off of the hasbro instructions found here: https://instructions.hasbro.com/en-my/instruction/connect-4-game
* The image below will be used as a demonstration and reference in development
![reference image](images/connect-4-board-reference.jpg)

**Technologies used:**
* Python
* Sockets

## Roadmap
* Client-Server architecture to ensure effective communication between server and clients
* A clear messaging protocol between server and client
* Server can handle multiple clients connecting and playing simultaneously, as well as disconnections
* Server can handle unexpected errors easily and informs the user an error has occurred, with a detailed explanation
* Code will be clean, commented, efficient, modular, and factored without duplicating code
* An easy to use UI, whether it be a GUI or CLI
* An accurate implementation of the Connect Four rules, as described by Hasbro

## Retrospective

***What went right:***
* Server/client communication
* Simultaneous client connections and games
* Client hosting and joining
* Game output and outcome
* Modularity of messages and generation/response

***What could be improved on:***
* Authentication of users
* Tracking of clients and the associated games
* Protocol for updating client games (reporting the entire history of moves akin to Forsyth–Edwards Notation in chess instead of the individual moves)
* Encryption of messages sent to/from client and server
* More user friendly and engaging UI instead of terminal graphics


**Known issues:**
* If user 1 hosts a game for user 2, and the game completes, the game will break if user 2 then hosts a game for user 1.
* If a user begins hosting a game, then aborts using keyboardInterrupt, their name will continue to appear in the join list despite being removed
