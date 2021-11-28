import control as ctrl 
import argparse
import socket
import threading
import time

class Vehicle( ctrl.VehicleControls) :
    def __init__(self, vehicle_id, host_address, listening_port, sending_port):
        super().__init__(vehicle_id, host_address, listening_port, sending_port)
    
    def deploy(self):
        return super().deploy()
        
    
def Main() :
    my_parser = argparse.ArgumentParser(description='command to execute the ./server script')
    my_parser.add_argument('--listen_port', help='listening_port', required=True)
    my_parser.add_argument('--sending_port', help='sending_port', required=True)
    args = my_parser.parse_args()
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    get_vehicle = Vehicle( 123, host, int(args.listen_port), int(args.sending_port))

    get_vehicle.deploy()

if __name__ == '__main__':
    Main()
