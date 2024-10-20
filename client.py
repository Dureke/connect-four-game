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

import clientmessage

sel = selectors.DefaultSelector()

def start_connections(server_addr, request):
    """Function called before the client event loop. Establishes connection to server."""
   
    print("starting connection to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    
    try: # make into loop to try 3 times before failing and stopping?
        errno = sock.connect_ex(server_addr)
    except Exception as err:
        print(f"Connection failed. [{errno}]:\n{err}.")
        sock.close()
        return

    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = clientmessage.Message(sel, sock, server_addr, request)
    sel.register(sock, events, data=message)

def send_new_message(socket, event, server_addr, request):
    message = clientmessage.Message(sel, socket, server_addr, request)
    socket.send()
            
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
    parser.add_argument('ip', metavar='ip-addr', type=str,
                        help='an IPv4/IPv6 address of the server the client is connecting to')
    parser.add_argument('port', type=int, 
                        help='the port of the server client is connecting to. Values within range [0, 65535]')
    parser.add_argument('action', metavar='request', type=str, 
                        help='the action requested from client to server')
    parser.add_argument('value', metavar='value', type=str, nargs='?',
                        help='the optional clarification for the action selected (Default: "None")')

    # TODO: Support DNS name and argument -d --DNS.

    args = vars(parser.parse_args())
    
    host = args['ip']
    port = args['port']
    if not 0 <= port <= 65535:
        raise ValueError(f"Invalid port value [{port}]. Port must be within range [0, 65535].")
    
    action = args['action']
    if not args['value']:
        value = "None"
    else:
        value = args['value']

    return host, port, action, value



# Start of the main program

host, port, action, value = parse_args()
request = clientmessage.create_request(action, value)
start_connections((host, port), request)

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()

        if not sel.get_map():
            break
except KeyboardInterrupt:
    print(f"Exception: Caught keyboard interrupt, exiting.")
except ConnectionError as err:
    print(f"Exception: Caught a connection error, exiting.\n{err}")
except Exception as err:
    print(f"Exception: Uncaught error, exiting.\n{err}.")
finally:
    sel.close()
    sys.exit(0)
