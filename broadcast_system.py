import json
import socket
import threading
import time
import geopy.distance
import math
import encryption


class HostConfigure:
    def __init__(self, host_address, port):
        self.host = host_address
        self.port = port


class BroadcastSystem(HostConfigure):
    def __init__(self, vehicle_id, host_address, port, sending_port, gps=None):
        super(BroadcastSystem, self).__init__(host_address, port)
        self.vehicle_id = vehicle_id
        self.pair_list = {}
        self.broadcast_port = 33341
        self.lock = threading.Lock()
        self.listening_port = port
        self.sending_port = sending_port
        self.gps = gps
        # TODO: replace above code with the self.GPS defined in the control.py
        self.sock = None
        self.route_table = {}

    def route_add(self, node_information):
        node = node_information['node']
        if node not in self.route_table.keys():
            node_gps = node_information['location']
            node_coordinate = (node_gps[0], node_gps[1])
            distance = geopy.distance.geodesic(self.gps, node_coordinate).meters
            print(self.gps, node_coordinate, distance)
            if distance < 20:
                self.route_table[node] = {'hop': 1, 'through': 'self'}

    def peer_list_updater(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(("", self.broadcast_port))
        while True:
            data = client.recvfrom(10240)
            decoded_data = json.loads(data[0].decode('utf-8'))
            node_id = decoded_data['node']
            peer_host = decoded_data['host']
            peer_port = int(decoded_data['port'])
            flag = [peer_host == self.pair_list[key].host and peer_port == self.pair_list[key].port for key in list(self.pair_list)]
            if not any(flag):
                self.lock.acquire()
                self.pair_list[node_id] = HostConfigure(peer_host, peer_port)
                print(f"index - {node_id} {self.pair_list[node_id]}")
                self.route_add(decoded_data)
                self.lock.release()
            print("PeerList-Starts----->")
            print([(self.pair_list[i].host, self.pair_list[i].port) for i in self.pair_list])
            print("PeerList-Ends---->")

    def broadcast_information(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # TODO: add custom message for infra (without gps data), can use the hasattr method
        message = {'node': self.vehicle_id, 'host': self.host, 'port': self.port, 'send_port': self.sending_port, 'location': self.gps}
        encode_data = json.dumps(message, indent=2).encode('utf-8')
        while True:
            server.sendto(encode_data, ('<broadcast>', self.broadcast_port))
            time.sleep(5)

    def information_listener(self, handler):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(32)
        # server.setblocking(False)     will try in selectors
        while True:
            conn, addr = server.accept()
            conn.setblocking(False)
            try:
                recv_data = conn.recv(10240)
                decrypt_data = encryption.do_decrypt(recv_data)
                print(f'decrypted data : {decrypt_data} from {addr}')
                handler(decrypt_data)
            except Exception as e:
                pass
                # print(f"error receiving {e} {addr}")
            conn.close()

    def send_information(self, data):
        time.sleep(2)
        delNode = []
        for peer in list(self.pair_list):
            peer_host = self.pair_list[peer].host
            peer_port = int(self.pair_list[peer].port)
            if self.host == peer_host and self.port == peer_port:
                continue
            enc_data = encryption.do_encrypt(data)
            # print(f"normal data {data}\n encrypted data {enc_data}")
            flag = self.send_messages(peer_host, peer_port, enc_data)
            print(f'Data send status : {flag}')
            if not flag and len(self.pair_list) > 1:
                # print(f"key {peer}")
                delNode.append(peer)
        self.reorder_pairlist(delNode)
        delNode.clear()
        time.sleep(7)

    def reorder_pairlist(self, delete_node):
        print(f"KEYS ---- {delete_node}")
        self.lock.acquire()
        for node in delete_node:
            pop = self.pair_list.pop(node)
            print(f"popped index {node} {pop}")
        self.lock.release()
        print([(self.pair_list[i].host, self.pair_list[i].port) for i in self.pair_list])

    def send_messages(self, host, port, data):
        server_address = (host, port)
        flag = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.sock.setblocking(False)
        self.sock.bind((self.host, self.sending_port))
        self.sock.connect_ex(server_address)
        try:
            self.sock.send(data)
            self.sock.close()
            return flag
        except Exception as e:
            print(f'{e} {server_address}')
            self.sock.close()
            return False

    def deploy(self, handler):
        server_thread = threading.Thread(target=self.broadcast_information)
        peer_thread = threading.Thread(target=self.peer_list_updater)
        info_thread = threading.Thread(target=self.information_listener, args=(handler,))
        # sensor_thread = threading.Thread(target=self.send_information, args=( sending_port,))

        server_thread.start()
        peer_thread.start()

        time.sleep(5)
        info_thread.start()

        # sensor_thread.start()
