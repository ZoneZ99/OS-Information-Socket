import sys
import socket as socket_lib
import selectors
import types

selector = selectors.DefaultSelector()


def accept_wrapper(socket: socket_lib.socket):
    connection, address = socket.accept()
    print(f"Connection accepted from {address}")
    connection.setblocking(False)
    data = types.SimpleNamespace(
        address=address,
        inputbyte=b'',
        outputbyte=b''
    )
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(connection, events, data=data)


def service_connection(key, mask):
    socket = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        received_data = socket.recv(1024)
        if received_data:
            received_data = received_data.upper()
            data.outputbyte += received_data
        else:
            print(f"Closing connection to {data.address}")
            selector.unregister(socket)
            socket.close()

    if mask & selectors.EVENT_WRITE:
        if data.outputbyte:
            sent = socket.send(data.outputbyte)
            data.outputbyte = data.outputbyte[sent:]


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)


host, port = sys.argv[1], int(sys.argv[2])

socket = socket_lib.socket(socket_lib.AF_INET, socket_lib.SOCK_STREAM)
socket.bind((host, port))
socket.listen()
print(f"Listening on {host}, {port}")
socket.setblocking(False)

selector.register(socket, selectors.EVENT_READ, data=None)

try:
    while True:
        events = selector.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print('Keyboard interrupt caught, exiting...')
finally:
    selector.close()