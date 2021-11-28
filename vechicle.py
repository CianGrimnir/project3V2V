import control as ctrl 
import argparse
import socket
import threading
import time

class Vehicle( ctrl.VehicleControls) :
    def __init__(self, vehicle_id, host_address, port):
        super().__init__(vehicle_id, host_address, port)
        
    
def Main() :
    my_parser = argparse.ArgumentParser(description='command to execute the ./server script')
    my_parser.add_argument('--listen_port', help='listening_port', required=True)
    my_parser.add_argument('--sending_port', help='sending_port', required=True)
    args = my_parser.parse_args()
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    get_vehicle = Vehicle( 123, host, int(args.listen_port))

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
    Main()
