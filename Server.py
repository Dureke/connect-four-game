import socket
import selectors
import types
import sys
import argparse

sel = selectors.DefaultSelector()

# initalizes the listening socket. Throws error if server_address is invalid
def setup_lsock(server_address):
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
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
    conn, addr = sock.accept()
    print(f"Address [{addr}] sucessfully connected.")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

# called when the server triggers a read or write invite event
def service_connection(key, mask):
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
    parser = argparse.ArgumentParser(prog='Server.py',
                                     description='This is the server portion of the connect four python game.')
    parser.add_argument('-i', '--ip-addr', metavar='IP', type=str, required=True, help='an IPv4/IPv6 address for server')
    parser.add_argument('-p', '--port', metavar='N', type=int, help='the port of the server')

    args = vars(parser.parse_args())
    
    host = args['ip-addr']
    if not args['port']:
        port = 65432
    else:
        port = args['port']
    
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