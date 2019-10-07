import sys
import socket as socket_lib
import selectors
import types

from urllib.error import URLError
from urllib.request import urlopen

import psutil

from cpuinfo import get_cpu_info


selector = selectors.DefaultSelector()


def get_argument_callbacks() -> dict:
    return {
        '--hw': get_hardware_info,
        '--mp': get_physical_memory_info,
        '--ms': get_swap_memory_info,
        '--storage': get_storage_info,
        '--netstat': get_connection_info,
        '--access': get_account_access_info,
        '--all': get_all_info
    }


def process_argument(argument: str) -> str:
    argument_callbacks = get_argument_callbacks()
    split_argument = argument.split(' ')

    returned_info = argument_callbacks.get(
        split_argument[0].lower(),
        lambda: "Invalid argument"
    )
    if returned_info == get_storage_info or returned_info == get_all_info:
        if len(split_argument) == 2:
            return returned_info(split_argument[1])
        else:
            return returned_info(path=".")
    else:
        return returned_info()


def get_hardware_info() -> str:
    cpu_info = get_cpu_info()
    default_message = "information not available"
    return f"\
        -- Hardware Info --\n\
        Architecture: {cpu_info.get('arch', default_message)}\n\
        Vendor: {cpu_info.get('vendor_id', default_message)}\n\
        Brand: {cpu_info.get('brand', default_message)}\n\
        Clock Speed: {cpu_info.get('hz_advertised', default_message)}\n\
        L1 Cache Size: {cpu_info.get('l1_data_cache_size', default_message)}\n\
        L2 Cache Size: {cpu_info.get('l2_cache_size', default_message)}\n\
        L3 Cache Size: {cpu_info.get('l3_cache_size', default_message)}"


def get_physical_memory_info() -> str:
    virtual_memory_info = psutil.virtual_memory()
    default_message = "information not available"
    return f"\
        -- Physical Memory Info --\n\
        Total Capacity: {getattr(virtual_memory_info, 'total', default_message)}\n\
        Used Capacity: {getattr(virtual_memory_info, 'used', default_message)}\n\
        Available Capacity: {getattr(virtual_memory_info, 'available', default_message)}"


def get_swap_memory_info() -> str:
    swap_memory_info = psutil.swap_memory()
    default_message = "information not available"
    return f"\
        -- Swap Memory Info --\n\
        Total Capacity: {getattr(swap_memory_info, 'total', default_message)}\n\
        Used Capacity: {getattr(swap_memory_info, 'used', default_message)}\n\
        Available Capacity: {getattr(swap_memory_info, 'free', default_message)}"


def get_storage_info(path: str) -> str:
    try:
        disk_usage = psutil.disk_usage(path)
        default_message = "information not available"
        return f"\
        -- Storage Usage of {path} --\n\
        Total Capacity: {getattr(disk_usage, 'total', default_message)}\n\
        Used Capacity: {getattr(disk_usage, 'used', default_message)}\n\
        Available Capacity: {getattr(disk_usage, 'free', default_message)}"
    except FileNotFoundError:
        return f"\
            -- Storage Usage of {path} --\n\
            Path {path} not found"


def get_connection_info() -> str:

    def check_connection() -> bool:
        try:
            urlopen('https://google.com')
            return True
        except URLError:
            return False

    return f"\
        -- Network Connection --\n\
        Status: {'connected' if check_connection() else 'not connected'}"


def get_account_access_info() -> str:
    # TODO IMPLEMENT
    return f"\
        -- Access Info -- NOT IMPLEMENTED YET"


def get_all_info(path: str) -> str:
    arguments_callbacks = get_argument_callbacks()
    arguments_keys = list(arguments_callbacks.keys())
    arguments_keys.pop(-1)

    returned_info = ""
    for argument in arguments_keys:
        callback = arguments_callbacks[argument]
        if callback == get_storage_info:
            returned_info += "\n" + callback(path)
        else:
            returned_info += "\n" + callback()
    return returned_info


def accept_wrapper(connection_socket: socket_lib.socket):
    connection, address = connection_socket.accept()
    print(f"Connection accepted from {address}")
    connection.setblocking(False)
    data = types.SimpleNamespace(
        address=address,
        inputbyte=b'',
        outputbyte=b''
    )
    connection_events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(connection, connection_events, data=data)


def service_connection(connection_key, connection_mask):
    connection_socket = connection_key.fileobj
    data = connection_key.data

    if connection_mask & selectors.EVENT_READ:
        received_data = connection_socket.recv(1024)
        if received_data:
            received_data = process_argument(received_data.decode('utf-8'))
            data.outputbyte += received_data.encode('utf-8')
        else:
            print(f"Closing connection to {data.address}")
            selector.unregister(connection_socket)
            connection_socket.close()

    if connection_mask & selectors.EVENT_WRITE:
        if data.outputbyte:
            sent = connection_socket.send(data.outputbyte)
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
