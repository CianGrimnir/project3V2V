import argparse
import json
import socket
import threading
import time

from sensor import Sensor


# lock = threading.RLock()


class HostConfigure:
    def __init__(self, host_address, port):
        self.host = host_address
        self.port = port


class BroadcastSystem(HostConfigure):
    def __init__(self, host_address, port):
        super(BroadcastSystem, self).__init__(host_address, port)
        self.pair_list = {}
        self.broadcast_port = 33341
        self.lock = threading.Lock()

    def peer_list_updater(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(("", self.broadcast_port))
        while True:
            data = client.recvfrom(1024)
            decoded_data = json.loads(data[0].decode('utf-8'))
            print(decoded_data)
            peer_host = decoded_data['host']
            peer_port = int(decoded_data['port'])
            flag = [peer_host == self.pair_list[key].host and peer_port == self.pair_list[key].port for key in list(self.pair_list)]
            print(f'flag {flag}')
            if any(flag):
                pass
            else:
                self.lock.acquire()
                index = peer_host + str(peer_port)
                self.pair_list[index] = HostConfigure(peer_host, peer_port)
                print(f'index - {index} {self.pair_list[index]}')
                self.lock.release()
            print([(self.pair_list[i].host, self.pair_list[i].port) for i in self.pair_list])

    def server_side(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = {'host': self.host, 'port': self.port}
        encode_data = json.dumps(message, indent=2).encode('utf-8')
        while True:
            server.sendto(encode_data, ('<broadcast>', self.broadcast_port))
            time.sleep(5)

    def information_listener(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(32)
        # server.setblocking(False)     will try in selectors
        while True:
            conn, addr = server.accept()
            conn.setblocking(False)
            try:
                recv_data = conn.recv(1024)
                decoded_data = recv_data.decode('utf-8')
                print(f'received data : {decoded_data} from {addr}')
            except Exception as e:
                pass
                # print(f'error receiving {e} {addr}')
            conn.close()

    def send_information(self, sending_port):
        while True:
            time.sleep(2)
            delNode = []
            for peer in list(self.pair_list):
                peer_host = self.pair_list[peer].host
                peer_port = int(self.pair_list[peer].port)
                if self.host == peer_host and self.port == peer_port:
                    continue
                node = Sensor()
                print("sending ...", peer_host, peer_port)
                message = f"sample {self.host} {self.port}"
                flag = node.send_messages(peer_host, peer_port, int(sending_port), message)
                print(f'data send status : {flag}')
                if not flag and len(self.pair_list) > 1:
                    print(f'key {peer}')
                    delNode.append(peer)
            self.reorder_pairlist(delNode)
            delNode.clear()
            time.sleep(7)

    def reorder_pairlist(self, delete_node):
        print(f'KEYS ---- {delete_node}')
        self.lock.acquire()
        for node in delete_node:
            pop = self.pair_list.pop(node)
            print(f'popped index {node} {pop}')
        self.lock.release()
        print([(self.pair_list[i].host, self.pair_list[i].port) for i in self.pair_list])


def main():
    my_parser = argparse.ArgumentParser(description='command to execute the ./server script')
    my_parser.add_argument('--listen_port', help='listening_port', required=True)
    my_parser.add_argument('--sending_port', help='sending_port', required=True)
    args = my_parser.parse_args()
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    get_vehicle = BroadcastSystem(host, int(args.listen_port))

    server_thread = threading.Thread(target=get_vehicle.server_side)
    peer_thread = threading.Thread(target=get_vehicle.peer_list_updater)
    info_thread = threading.Thread(target=get_vehicle.information_listener)
    sensor_thread = threading.Thread(target=get_vehicle.send_information, args=(args.sending_port,))

    server_thread.start()
    peer_thread.start()

    time.sleep(5)
    info_thread.start()

    sensor_thread.start()


if __name__ == '__main__':
    main()
