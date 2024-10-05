# Connect Four Python Game with Sockets

This is a simple Connect Four game implemented using Python and sockets.
**How to run:**
1. **Start the server:** Run the `Server.py` script with -i arg set to an IP address. There is an optional arg -p/--port, default value set to 65432. Example: `py Server.py -i 127.0.0.1` or `py Server.py -i 127.0.0.1 -p 65432`
2. **Start one or more clients:** Run the `Client.py` script with -i arg set to the server IP address. There is an optional arg -p/--port, default value set to 65432. Example: `py Client.py -i 127.0.0.1` or `py Client.py -i 127.0.0.1 -p 65432`
3. **Write messages to Server**: In the client terminal, type a variety of messages, seperated by ENTER key. When finished, type 'quit' and press ENTER. Server will echo the messages sent. Multiple clients can do this simultanously.

**How to play:**
1. **Start the server:** Run the `Server.py` script.
2. **Connect clients:** Run the `Client.py` script on two different machines or terminals.
3. **Play the game:** Players take turns entering their moves. The first player to connect four in their color wins!

**Rules:** 
* One of the two players will be chosen at random to make the first move
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
