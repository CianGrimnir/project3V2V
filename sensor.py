import socket

class Sensor:
    def __init__(self):
        self.speed = 0
        self.proximity = 0
        sock = None

    def send_messages(self, host, port, data):
        server_address = (host, port)
        flag = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(server_address)
        try:
            self.sock.send(data.encode('utf-8'))
        except Exception as e:
            print(f'{e} {server_address}')
            return False