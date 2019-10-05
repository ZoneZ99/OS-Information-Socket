import sys
import socket as socket_lib
import selectors
import types


selector = selectors.DefaultSelector()


def start_connections(host, port, argument):
    pass


def service_connection(key, mask):
    pass


if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0] <host> <port> <argument>}")
    sys.exit(1)

host, port, argument = sys.argv[1:4]
start_connections(host, int(port), argument)

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
