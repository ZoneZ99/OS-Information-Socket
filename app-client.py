import sys
import socket as socket_lib
import selectors
import types


selector = selectors.DefaultSelector()


def start_connection(host, port, argument):
    server_address = (host, port)
    print(f"Starting connection to {server_address}")
    socket = socket_lib.socket(socket_lib.AF_INET, socket_lib.SOCK_STREAM)
    socket.setblocking(False)
    socket.connect_ex(server_address)

    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(
        argument=argument,
        outputbyte=b'',
        sent=False,
        received=False,
    )

    selector.register(socket, events, data=data)


def service_connection(key, mask):
    socket = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        received_data = socket.recv(1024)
        if received_data:
            print(f"Received: {repr(received_data)}")
            data.received = True

        if not received_data or data.received:
            print("Closing connection...")
            selector.unregister(socket)
            socket.close()

    if mask & selectors.EVENT_WRITE:
        if not data.outputbyte:
            data.outputbyte = data.argument.encode('utf-8')

        if data.outputbyte and not data.sent:
            print(f"Sending {repr(data.outputbyte)} to connection...")
            sent = socket.send(data.outputbyte)
            data.outputbyte = data.outputbyte[sent:]
            data.sent = True


if len(sys.argv) != 4:
    print(
        f"Usage: {sys.argv[0]} <host> <port> <argument>\n\
        Run with --help argument to see a list of available arguments"
    )
    sys.exit(1)

host, port, argument = sys.argv[1:4]
start_connection(host, int(port), argument)

try:
    while True:
        events = selector.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        if not selector.get_map():
            break
except KeyboardInterrupt:
    print('Keyboard interrupt caught, exiting...')
finally:
    selector.close()
