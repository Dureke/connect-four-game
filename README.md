# Connect Four Python Game with Sockets

This is a simple Connect Four game implemented using Python and sockets.
**How to run:**
1. **Start the server:** Run the `Server.py` script with 2 optional arguments.
   - usage: server.py [-h\] -i ip-addr -p [port\]
   - First optional arg is the server IP address, default value set to 0.0.0.0.
   - Second optional arg is the port number of the server, default value set to 65432.
   - Example: `py Server.py -i 127.0.0.1 -p 65432` is equivalent to `py Server.py -p 65432`.
   - Use `py Server.py -h` for additional information.
     
3. **Start one or more clients:** Run the `Client.py` script with 4 optional arguments.
   - usage: Client.py [-h\] -i ip-addr -p port login username
   - First optional arg is the the server IP address, default value set to 127.0.0.1.
   - Second optional arg is the port number of the server the client is connecting to, default value set to 65432.
   - Third optional arg is the command login, default is set to login.
   - Forth optional arg is the username that you'd login as, default is set to user#, where # changes by the number of users.
   - Example: `py Client.py 127.0.0.1 65432 login username` or `py Client.py 127.0.0.1 65432 login testUser`.
   - Use `py Client.py -h` for additional information.
     
4. **Write messages to Server**: In the client terminal, follow the prompts given by the client text application. If there is another game hosted by another client, the join action will work. Otherwise, you can create a game with create or quit and disconnect with the quit action.

Example Series of Inputs:
- Run `py server.py 127.0.0.1 65432`
- Run `py client.py 127.0.0.1 65432 login user1`
- Run `py client.py 127.0.0.1 65432 login user2`
- In terminal with user1, type `start`
- In terminal with user2, type `join`
- In terminal with user2, type `user1`
- In terminal with user1, give a move (This can by anything at the moment)

The clients will periodically ask the server for updates on the board, as well as letting the clients know whose turn it is. After a user makes a move, the server will swap whose turn it is, letting the other client know it can make a move. There's a bug that is causing the same user to repeatively make a move. This will be fixed in a later update.

~~**How to play:**~~
~~1. **Start the server:** Run the `Server.py` script.~~
~~2. **Connect clients:** Run the `Client.py` script on two different machines or terminals.~~
~~3. **Play the game:** Players take turns entering their moves. The first player to connect four in their color wins!~~

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
