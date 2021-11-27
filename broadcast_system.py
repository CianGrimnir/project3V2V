import argparse
import json
import socket
import threading
import time

from sensor import Sensor

broadcast_port = 33341
pair_list = {}
index = 1
#lock = threading.RLock()
lock = threading.Lock()


class HostConfigure:
    def __init__(self, hostaddress, port):
        self.host = hostaddress
        self.port = port


def peer_list_updater(BPORT):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 33341))
    global index
    while True:
        data = client.recvfrom(1024)
        decoded_data = json.loads(data[0].decode('utf-8'))
        print(decoded_data)
        flag = [decoded_data['host'] == pair_list[key].host and decoded_data['port'] == pair_list[key].port for key in
                list(pair_list)]
        if any(flag):
            pass
        else:
            lock.acquire()
            pair_list[index] = HostConfigure(decoded_data['host'], decoded_data['port'])
            lock.release()
            index += 1
        print([(pair_list[i].host, pair_list[i].port) for i in pair_list])


def server_side(host, BPORT, LPORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = {'host': host, 'port': LPORT}
    encode_data = json.dumps(message, indent=2).encode('utf-8')
    while True:
        server.sendto(encode_data, ('<broadcast>', BPORT))
        time.sleep(5)


def information_listener(host, LPORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(host, LPORT)
    server.bind((host, LPORT))
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
            #print(f'error receiving {e} {addr}')
        conn.close()


def send_information(selfaddress, sending_port):
    while True:
        time.sleep(2)
        for peer in list(pair_list):
            peerHost = pair_list[peer].host
            peerPort = int(pair_list[peer].port)
            if host == selfaddress.host and selfaddress.port == peerPort:
                continue
            node = Sensor()
            print("sending ...",peerHost, peerPort)
            message = f"sample {host} {args.listen_port}"
            flag = node.send_messages(peerHost, peerPort, sending_port, message)
            print(f'data send status : {flag}')
            if not flag and len(pair_list) > 1:
                print(f'key {peer}')
                pop = pair_list.pop(peer)
                lock.acquire()
                reorder_pairlist()
                lock.release()
        time.sleep(7)


def reorder_pairlist():
    keys = list(pair_list.keys())
    print(keys)
    temp = {}
    global index
    lock.acquire()
    for i in range(len(pair_list)):
        temp[i] = pair_list[keys[i]]
    lock.release()
    index = len(pair_list)
    print(pair_list, index)


my_parser = argparse.ArgumentParser(description='command to execute the ./server script')
my_parser.add_argument('--listen_port', help='listening_port', required=True)
my_parser.add_argument('--sending_port', help='sending_port', required=True)
args = my_parser.parse_args()
hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
selfinfo = HostConfigure(host, int(args.listen_port))
pair_list[0] = HostConfigure(host, args.listen_port)
serverThread = threading.Thread(target=server_side, args=(host, broadcast_port, args.listen_port,))
peerThread = threading.Thread(target=peer_list_updater, args=(broadcast_port,))
infoThread = threading.Thread(target=information_listener, args=(host, int(args.listen_port),))
sensorThread = threading.Thread(target=send_information, args = (selfinfo,int(args.sending_port,)))

serverThread.start()
peerThread.start()

time.sleep(5)
infoThread.start()

sensorThread.start()
