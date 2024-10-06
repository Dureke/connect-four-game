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
import types
import argparse

sel = selectors.DefaultSelector()
messages = [b"This is the start of the connection."]

def start_connections(server_addr):
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
    data = types.SimpleNamespace(
        msg_total=sum(len(m) for m in messages),
        recv_total=0,
        messages=list(messages),
        outb=b"",
        end_conn=False,
    )
    sel.register(sock, events, data=data)


def service_connection(key, mask):
    """Function called when a client triggers a read or write event."""
    sock = key.fileobj
    data = key.data

    # populate messages with the text that you want to send
    while not data.end_conn:
        data.messages.append(input().encode(encoding="utf-8"))
        data.msg_total += len(data.messages[-1])
        if data.messages[-1] == b"quit":
            data.end_conn = True

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print("received", repr(recv_data), "from connection")
            data.recv_total += len(recv_data)

        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection. Goodbye!")
            sel.unregister(sock)
            sock.close()
            return
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {repr(data.outb)} to connection.")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
            
# parses the required argument of --ip-addr, as well as an optional port number
def parse_args():
    """Function neatly takes sys.argv arguments and outputs returns host, port based on the input values.
    If there is additional unexpected arguments, an error is thrown and program is prematurely ended.
    
    Returns: host, port
    Example: ('127.0.0.1', 65432)
    
    Accepted arguments: -i/--ip-addr (str: IPv4/IPv6), -p/--port (int: 0-65535)"""
    parser = argparse.ArgumentParser(prog='Client.py',
                                     description='This is the client portion of the connect four python game.')
    parser.add_argument('-i', '--ip', metavar='IP', type=str, required=True, help='an IPv4/IPv6 address of the server the client is connecting to')
    parser.add_argument('-p', '--port', metavar='N', type=int, help='the port of the server client is connecting to')

    args = vars(parser.parse_args())
    
    host = args['ip']
    if not args['port']:
        port = 65432
    else:
        port = args['port']
        if not 0 <= port <= 65535:
            print(f"Exception: Port must be within range [0, 65535]")
            sys.exit(1)
    
    return host, port

# Start of the main program

host, port = parse_args()
start_connections((host, port))

try:
    while True:
        events = sel.select(timeout=None)
        if events:
            for key, mask in events:
                service_connection(key, mask)

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
