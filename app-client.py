import sys
import socket as socket_lib
import selectors
import types


selector = selectors.DefaultSelector()


def start_connection(host='', port=None, argument=''):
    server_address = (host, port)
    print(f"Starting connection to {server_address}")
    socket = socket_lib.socket(socket_lib.AF_INET, socket_lib.SOCK_STREAM)
    socket.setblocking(False)
    socket.connect_ex(server_address)

    connection_events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(
        argument=argument,
        outputbyte=b'',
        sent=False,
        received=False,
    )

    selector.register(socket, connection_events, data=data)


def service_connection(connection_key, connection_mask):
    socket = connection_key.fileobj
    data = connection_key.data

    if connection_mask & selectors.EVENT_READ:
        received_data = socket.recv(1024)
        if received_data:
            print(f"Received: \n{received_data.decode('utf-8')}")
            data.received = True

        if not received_data or data.received:
            print("Closing connection...")
            selector.unregister(socket)
            socket.close()

    if connection_mask & selectors.EVENT_WRITE:
        if not data.outputbyte:
            data.outputbyte = data.argument.encode('utf-8')

        if data.outputbyte and not data.sent:
            print(f"Sending {data.outputbyte.decode('utf-8')} to connection...")
            sent = socket.send(data.outputbyte)
            data.outputbyte = data.outputbyte[sent:]
            data.sent = True


if len(sys.argv) == 2 and sys.argv[-1] == "--help":
    print('''
    Usage: app-client.py <host> <port> [<argument>]
    List of available arguments:
    --hw                    : Get CPU informations
    --mp                    : Get physical memory informations
    --ms                    : Get swap memory informations
    --storage [<directory>] : Get storage informations from given <directory>, defaults to "."
    --netstat               : Get server connectivity information
    --access                : Get account access information
    --all [<directory>]     : Get all of the above informations
    ''')
    sys.exit(1)

if len(sys.argv) < 3:
    print(
        f"Usage: {sys.argv[0]} <host> <port> [<argument>]\n\
        Run with --help argument to see a list of available arguments"
    )
    sys.exit(1)

if len(sys.argv) >= 3:
    start_connection(
        host=sys.argv[1],
        port=int(sys.argv[2]),
        argument=' '.join(sys.argv[3:])
    )

try:
    while True:
        events = selector.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        if not selector.get_map():
            break
except ConnectionRefusedError:
    print('Server is offline')
except KeyboardInterrupt:
    print('Keyboard interrupt caught, exiting...')
finally:
    selector.close()
