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
import types
import sys
import argparse

sel = selectors.DefaultSelector()

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
        print(f"Exception: Input address [{server_address}] not valid, exiting.")
        sys.exit(1)
    lsock.listen()
    print(f"listening on {server_address}.")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

# server accepting a client and listening to it
def accept_wrapper(sock):
    """Function called when client is trying to connect to server. Establishes connection and registers client socket.
    Logs a sucessful connection into the terminal.

    Arguments: key.fileobj  sock
    Example:   selectors.selector().SelectorKey.fileobj"""
    conn, addr = sock.accept()
    print(f"Address [{addr}] sucessfully connected.")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

# called when the server triggers a read or write invite event
def service_connection(key, mask):
    """Function called when server triggers a read or write event. Processes recieved data from
    client and echoes recieved data back to the client.
    Logs sent data into terminal. If no more data is recieved, closes connection to client.
    
    Arguments: selectors SelectorKey, 
               selectors _EventMask
    Example:   key, mask = selectors.selector()"""
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print(f"No more data from {data.addr}. Connection ended.")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"echoing {repr(data.outb)} to {data.addr}.")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

# parses the required argument of --ip-addr, as well as an optional port number
def parse_args():
    """Function neatly takes sys.argv arguments and outputs returns host, port based on the input values.
    If there is additional unexpected arguments, an error is thrown and program is prematurely ended.
    
    Returns: host, port
    Example: ('127.0.0.1', 65432)
    
    Accepted arguments: -i/--ip-addr (str: IPv4/IPv6), -p/--port (int: 0-65535)"""
    parser = argparse.ArgumentParser(prog='Server.py',
                                     description='This is the server portion of the connect four python game.')
    parser.add_argument('-i', '--ip', metavar='IP', type=str, required=True, help='an IPv4/IPv6 address for server')
    parser.add_argument('-p', '--port', metavar='N', type=int, help='the port of the server')

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
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print(f"Exception: Caught keyboard interrupt, exiting.")
except ConnectionError as err:
    print(f"Exception: Caught a connection error, exiting.\n{err}")
except Exception as err:
    print(f"Exception: Uncaught error.\n{err}.")
finally:
    sel.close()
    sys.exit(0)