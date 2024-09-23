# Connect Four Python Game with Sockets

This is a simple Connect Four game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
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
