
import sys
import socket
import selectors
import types
import argparse

sel = selectors.DefaultSelector()
messages = [b"This is the start of the connection."]

# this routine is called to create each of the many ECHO CLIENTs we want to create
def start_connections(server_addr):
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


# this routine is called when a client triggers a read or write event
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    # populate messages with the text that you want to send
    while not data.end_conn:
        data.messages.append(input().encode(encoding="utf-8"))
        data.msg_total += len(data.messages[-1])
        # print(f"Added {data.messages[-1]} with length {len(data.messages[-1])} to msg_total.")
        # print(f"Messages now contains {data.messages}.")
        if data.messages[-1] == b"quit":
            data.end_conn = True

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data), "from connection")
            data.recv_total += len(recv_data)

        # print(f"Recovered data total: [{data.recv_total}]. Total: [{data.msg_total}]")
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection. Goodbye!")
            sel.unregister(sock)
            sock.close()
            return
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            # print(f"data.outb {data.outb}. data.messages {data.messages}")
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {repr(data.outb)} to connection.")
            sent = sock.send(data.outb)
            # print(f"Sent: {sent}. Outb Len: {len(data.outb)}")
            # print(f"Test: {data.outb[sent:]}")
            data.outb = data.outb[sent:]
            
# parses the required argument of --ip-addr, as well as an optional port number
def parse_args():
    parser = argparse.ArgumentParser(prog='Client.py',
                                     description='This is the client portion of the connect four python game.')
    parser.add_argument('-i', '--ip-addr', metavar='IP', type=str, required=True, help='an IPv4/IPv6 address of the server the client is connecting to')
    parser.add_argument('-p', '--port', metavar='N', type=int, help='the port of the server client is connecting to')

    args = vars(parser.parse_args())
    
    host = args['ip-addr']
    if not args['port']:
        port = 65432
    else:
        port = args['port']
    
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
