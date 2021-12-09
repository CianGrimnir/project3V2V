import json
import socket
import threading
import time
import geopy.distance
import encryption
import struct
import logging

logging.basicConfig(format='%(asctime)-15s  %(message)s', level=logging.INFO)
logger = logging.getLogger('v2vnode')

# Multicast address for broadcasting the routing table.
# If other pi is not receiving the broadcast, increase the TTL
MCAST_TTL = 1
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 34599


class HostConfigure:
    """
    This class acts as the shell for storing peer details
    """

    def __init__(self, host_address: str, port: int):
        """
        Initializer for the shell class.
        :param host_address: ip address of the host.
        :param port: port number of the host.
        """
        self.host = host_address
        self.port = port


class BroadcastSystem(HostConfigure):
    """
    This class acts as the communication system/router for the Vehicle or Infra.
    """
    def __init__(self, vehicle_id: int, host_address: str, port: int, sending_port: int, gps: tuple = None):
        """
        Initializer for the communication system.
        :param vehicle_id: id of the vehicle/infra node.
        :param host_address: ip address of the node
        :param port: listening port of the node.
        :param sending_port: port to be used while sending a data.
        :param gps: GPS coordinates of the node.
        """
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
        self.route_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.get_route_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.route_table = {}

    def route_add(self, node_information: dict):
        """
        Add new entry to the routing table.
        :param node_information: remote node information received from broadcast.
        """
        node = node_information['node']
        if node not in self.route_table.keys():
            node_gps = node_information['location']
            node_coordinate = (node_gps[0], node_gps[1])
            distance = geopy.distance.geodesic(self.gps, node_coordinate).meters
            logger.debug(self.gps, node_coordinate, distance)
            if distance < 20:
                self.route_table[node] = {'hop': 1, 'through': 'self'}
                logger.info(f"ROUTE TABLE UPDATE : {self.route_table}")
                self.broadcast_route_table()

    def receive_route(self):
        """
        Receive route table from the neighbouring nodes.
        """
        self.get_route_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.get_route_sock.bind(('', MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        self.get_route_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        while True:
            table, addr = self.get_route_sock.recvfrom(10240)
            decoded_table = json.loads(table, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
            logger.debug(f"DECODED TABLE from {addr} - {decoded_table}")
            if decoded_table['node'] not in self.route_table.keys():
                continue
            update_flag = False
            for node in decoded_table['route']:
                if node == self.vehicle_id:
                    continue
                new_hop = decoded_table['route'][node]['hop'] + 1
                # through = self.get_node_id(addr)
                through = decoded_table['node']
                if node not in self.route_table.keys():
                    self.route_table[node] = {'hop': new_hop, 'through': through}
                    update_flag = True
                elif new_hop < self.route_table[node]['hop']:
                    self.route_table[node] = {'hop': new_hop, 'through': through}
                    update_flag = True
            self.check_null_route(decoded_table)
            if update_flag:
                self.broadcast_route_table()

    def check_null_route(self, remote_route_table: dict):
        """
        Check for null/old non-existent routes in the neighbours routing table.
        If null route exist, remove the entry from the self routing table.
        :param remote_route_table: route table of the neighbouring node.
        """
        remove_route = []
        route_through_node = [i for i in self.route_table if self.route_table[i]['through'] == remote_route_table['node']]
        nodes = list(remote_route_table['route'].keys())
        for node in route_through_node:
            if node not in nodes:
                remove_route.append(node)
        self.route_delete(remove_route)

    def get_node_id(self, remote_addr: tuple):
        """
        Return the node id from remote ip address and port number.
        :param remote_addr: ip address and port number of the remote node.
        :return: int: id of the resulting node.
        """
        for node in list(self.pair_list):
            if remote_addr[0] == self.pair_list[node].host and int(remote_addr[1]) == self.pair_list[node].port:
                return node

    def broadcast_route_table(self):
        """
        Broadcast route table to neighbouring nodes.
        """
        self.route_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MCAST_TTL)
        send_route_db = {'node': self.vehicle_id, 'route': self.route_table}
        route_table_json = json.dumps(send_route_db)
        self.route_sock.sendto(route_table_json.encode('utf-8'), (MCAST_GRP, MCAST_PORT))

    def route_delete(self, node_list):
        """
        Remove unreachable routes from the route table.
        :param node_list: nodes to be removed from the route table.
        """
        if not node_list:
            return
        self.lock.acquire()
        for node in node_list:
            try:
                pop = self.route_table.pop(node)
                logger.info(f"popped route {node} {pop}")
            except KeyError as e:
                pass
        self.lock.release()
        logger.info(f"updated route_table {self.route_table}")
        self.broadcast_route_table()

    def peer_list_updater(self):
        """
        Discover neighbouring nodes using broadcast system and update the route table
        and pair_list - maintaining the neighbours' node information.
        """
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
                logger.info(f"index - {node_id} {self.pair_list[node_id]}")
                self.route_add(decoded_data)
                self.lock.release()
            logger.info("PeerList-Starts----->")
            logger.info([(self.pair_list[i].host, self.pair_list[i].port) for i in self.pair_list])
            logger.info("PeerList-Ends---->")

    def broadcast_information(self):
        """
        Broadcast self information to the neighbouring nodes.
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # TODO: add custom message for infra (without gps data), can use the hasattr method
        message = {'node': self.vehicle_id, 'host': self.host, 'port': self.port, 'send_port': self.sending_port, 'location': self.gps}
        encode_data = json.dumps(message, indent=2).encode('utf-8')
        while True:
            server.sendto(encode_data, ('<broadcast>', self.broadcast_port))
            time.sleep(5)

    def information_listener(self, handler):
        """
        Receive sensor information from neighbouring nodes.
        :param handler:  handler function to process the received readings.
        """
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
                logger.info(f'decrypted data : {decrypt_data} from {addr}')
                if 'relay' in decrypt_data.keys():
                    record = self.route_table[decrypt_data['relay']]
                    if record['through'] == 'self':
                        node = record['node']
                        decrypt_data.pop('relay')
                    else:
                        node = record['through']
                    peer_host = self.pair_list[node].host
                    peer_port = self.pair_list[node].port
                    flag = self.send_messages(peer_host, peer_port, recv_data)
                handler(decrypt_data)
            except Exception as e:
                pass
                # logger.error(f"error receiving {e} {addr}")
            conn.close()

    def send_information(self, data):
        """
        Send sensor readings to all neighbouring nodes using pair_list and route table.
        :param data: sensor readings.
        """
        time.sleep(2)
        delNode = []
        for peer in list(self.pair_list):
            peer_host = self.pair_list[peer].host
            peer_port = int(self.pair_list[peer].port)
            if self.host == peer_host and self.port == peer_port:
                continue
            node_id = self.get_node_id((peer_host, peer_port))
            try:
                record = self.route_table[node_id]
            except KeyError as e:
                continue
            if record['through'] != 'self':
                next_hop = record['through']
                peer_host = self.pair_list[next_hop].host
                peer_port = self.pair_list[next_hop].port
                if isinstance(data, str):
                    data = json.loads(data)
                data.update({'relay': node_id})
            data = json.dumps(data)
            enc_data = encryption.do_encrypt(data)
            logger.debug(f"normal data {data}\n encrypted data {enc_data}")
            flag = self.send_messages(peer_host, peer_port, enc_data)
            if not flag and len(self.pair_list) > 1:
                logger.debug(f"key {peer}")
                delNode.append(peer)
        self.reorder_pairlist(delNode)
        self.route_delete(delNode)
        delNode.clear()
        time.sleep(7)

    def reorder_pairlist(self, delete_node):
        """
        Remove inactive nodes from pair_list.
        :param delete_node: inactive nodes.
        """
        self.lock.acquire()
        for node in delete_node:
            pop = self.pair_list.pop(node)
            logger.info(f"popped index {node} {pop}")
        self.lock.release()
        logger.info([(self.pair_list[i].host, self.pair_list[i].port) for i in self.pair_list])

    def send_messages(self, host, port, data):
        """
        Send encrypted data to mentioned host and pair.
        :param host: ip address of the neighbouring node.
        :param port: port number of the neighbouring node.
        :param data: encrypted data to send.
        :return: status code of the message sent.
        """
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
            logger.debug(f'{e} {server_address}')
            self.sock.close()
            return False

    def deploy(self, handler):
        """
        deploy the communication modules.
        :param handler: handler method to process received data.
        """
        server_thread = threading.Thread(target=self.broadcast_information)
        peer_thread = threading.Thread(target=self.peer_list_updater)
        route_thread = threading.Thread(target=self.receive_route)
        info_thread = threading.Thread(target=self.information_listener, args=(handler,))
        # sensor_thread = threading.Thread(target=self.send_information, args=( sending_port,))

        server_thread.start()
        peer_thread.start()
        # TODO: do we require this part for infra as well? If yes, we have to update the infra class with GPS data
        route_thread.start()
        time.sleep(15)
        info_thread.start()

        # sensor_thread.start()
