"""
This is the application that starts-up the server and listens for client connections.

usage: Server.py [-h] -i IP [-p N]

This is the server portion of the connect four python game.

options:
  -h, --help      show this help message and exit
  -i IP, --ip IP  an IPv4/IPv6 address for server
  -p N, --port N  the port of the server
"""

import socket
import selectors
import sys
import argparse
import traceback
import logging

from server_package.connection import Connection
import game.movehandler as movehandler

sel = selectors.DefaultSelector()
players = []
games = []
connections = {} # player : board


logging.basicConfig(level=logging.DEBUG)

def setup_lsock(server_address):
    """Function called before the server event loop. Establishes server listening socket.
    Throws error if server_address provided is invalid. Logs a sucessful setup in the terminal.
    
    Arguments: tuple (host, port)
    Example:   ('127.0.0.1', 65432)"""

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind(server_address)
    except socket.error:
        logging.exception(f"Exception: Input address [{server_address}] not valid, exiting.")
        sys.exit(1)
    lsock.listen()
    logging.info(f"listening on {server_address}.")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

# server accepting a client and listening to it
def accept_wrapper(sock):
    """Function called when client is trying to connect to server. Establishes connection and registers client socket.
    Logs a sucessful connection into the terminal.

    Arguments: key.fileobj  sock
    Example:   selectors.selector().SelectorKey.fileobj"""

    conn, addr = sock.accept()
    logging.info(f"Address [{addr}] sucessfully connected.")
    conn.setblocking(False)
    connection = Connection(sel, conn, addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=connection)
    connections[addr] = connection

# parses the required argument of --ip-addr, as well as an optional port number
def parse_args():
    """Function neatly takes sys.argv arguments and outputs returns host, port based on the input values.
    If there is additional unexpected arguments, an error is thrown and program is prematurely ended.
    
    Returns: host, port
    Example: ('127.0.0.1', 65432)
    
    usage: Server.py [-h] ip-addr [port]"""
    parser = argparse.ArgumentParser(prog='Server.py',
                                     description='This is the server portion of the connect four python game.')
    parser.add_argument('ip', metavar='ip-addr', type=str, 
                        help='an IPv4/IPv6 address for server')
    parser.add_argument('port', type=int, nargs='?',
                        help='the port of the server. Values within range [0, 65535] (Default: 65432)')

    args = vars(parser.parse_args())
    
    host = args['ip']
    if not args['port']:
        port = 65432
    else:
        port = args['port']
        if not 0 <= port <= 65535: ## TODO: should move exception to setup_lsock? 
            raise ValueError(f"Invalid port value [{port}]. Port must be within range [0, 65535].")
    
    return host, port

# Start of the main program

host, port = parse_args()
setup_lsock((host, port))

try:
    while True:
        # Global tasks, assigning tasks given by its branching connections. Updates games, tells which connections need updating
        movehandler.handle_moves()
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                """
                If this connection needs to be updated, then tell this connection to update its client connection
                Then, continue normal process of reading/writing
                """
                connection = key.data
                try:
                    connection.process_events(mask)
                except Exception:
                    logging.exception(f"Exception: exception for {connection.addr}:\n{traceback.format_exc()}")
                    connection.close()
                    connections[connection.get_address()] = None
except KeyboardInterrupt:
    logging.exception(f"Exception: Caught keyboard interrupt, exiting.")
except ConnectionError as err:
    logging.exception(f"Exception: Caught a connection error, exiting.\n{err}")
except Exception as err:
    logging.exception(f"Exception: Uncaught error.\n{err}.")
finally:
    sel.close()
    sys.exit(0)
