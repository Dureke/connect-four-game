"""
This is the application that connects to a host server and port.

usage: Client.py [-h] -i IP [-p N]

This is the client portion of the connect four python game.

options:
-h, --help           show this help message and exit
-i IP, --ip IP       an IPv4/IPv6 address of the server the client is connecting to
-p N, --port N       the port of the server client is connecting to
"""

import sys
import socket
import selectors
import struct
import argparse
import traceback
import logging
import random

from client_package.connection import Connection 

sel = selectors.DefaultSelector()
logging.basicConfig(level=logging.DEBUG)


def start_connections(server_addr, username):
    """Function called before the client event loop. Establishes connection to server."""
   
    logging.info(f"starting connection to {server_addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    
    try: # make into loop to try 3 times before failing and stopping?
        errno = sock.connect_ex(server_addr)
    except Exception as err:
        logging.exception(f"Connection failed. [{errno}]:\n{err}.")
        sock.close()
        return

    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    connection = Connection(sel, sock, server_addr, username)
    sel.register(sock, events, data=connection)
            
# parses the required argument of --ip-addr, as well as an optional port number
def parse_args():
    """Function neatly takes sys.argv arguments and outputs returns host, port based on the input values.
    If there is additional unexpected arguments, an error is thrown and program is prematurely ended.
    
    Returns: host, port, action, value
    Example: ('127.0.0.1', 65432, 'search', 'user')
    
    usage: Client.py [-h] ip-addr port request [value]
    examp: Client.py 127.0.0.1  65432 search user"""
    parser = argparse.ArgumentParser(prog='Client.py',
                                     description='This is the client portion of the connect four python game.')
    parser.add_argument('-i', '--ip', type=str,
                        help='an IPv4/IPv6 address of the server the client is connecting to')
    parser.add_argument('-p', '--port', type=int, 
                        help='the port of the server client is connecting to. Values within range [0, 65535]')
    parser.add_argument('action', metavar='request', type=str, nargs='?',
                        help='the action requested from client to server. Actions possible: [\'login\']')
    parser.add_argument('value', metavar='value', type=str, nargs='?',
                        help='the optional clarification for the action selected (Default: "user#")')

    args = vars(parser.parse_args())
    
    if not args['ip']:
        host = '127.0.0.1'
    else:
        host = args['ip']

    if not args['port']:
        port = 65432
    else:
        port = args['port']
        if not 0 <= port <= 65535:
            raise ValueError(f"Invalid port value [{port}]. Port must be within range [0, 65535].")
    
    if not args['action']:
        action = 'login'
    else:
        action = args['action']

    if not args['value']:
        value = f"user{random.randint(0,1000)}"
    else:
        value = args['value']

    return host, port, action, value



# Start of the main program

host, port, action, value = parse_args()
# request = clientmessage.create_request(action, value)
start_connections((host, port), value)

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            connection = key.data
            try:
                connection.process_events(mask)
            except Exception:
                logging.exception(f"main: error: exception for {connection.addr}:\n{traceback.format_exc()}")
                connection.close()

        if not sel.get_map():
            break
except KeyboardInterrupt:
    logging.exception(f"Exception: Caught keyboard interrupt, exiting.")
except ConnectionError as err:
    logging.exception(f"Exception: Caught a connection error, exiting.\n{err}")
except Exception as err:
    logging.exception(f"Exception: Uncaught error, exiting.\n{err}.")
finally:
    sel.close()
    sys.exit(0)
