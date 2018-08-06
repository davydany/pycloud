import socket

def is_port_open(host, port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    return result == 0 # True if result is 0, else False

