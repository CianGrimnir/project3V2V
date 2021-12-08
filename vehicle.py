import control as ctrl
import argparse
import socket
import threading
import time


class Vehicle(ctrl.VehicleControls):
    def __init__(self, vehicle_id, host_address, listening_port, sending_port, latitude, longitude):
        super().__init__(vehicle_id, host_address, listening_port, sending_port, latitude, longitude)

    def deploy(self):
        return super().deploy()


class Infra(ctrl.InfraControls):
    def __init__(self, vehicle_id, host_address, listening_port, sending_port):
        super().__init__(vehicle_id, host_address, listening_port, sending_port)

    def deploy(self):
        return super().deploy()


def main():
    my_parser = argparse.ArgumentParser(description='command to execute the ./server script')
    my_parser.add_argument('--listen_port', help='listening_port', required=True)
    my_parser.add_argument('--sending_port', help='sending_port', required=True)
    my_parser.add_argument('--latitude', help='latitude location', required=True)
    my_parser.add_argument('--longitude', help='longitude location', required=True)
    my_parser.add_argument('--vehicle_id', help='vehicle_id', required=True)
    my_parser.add_argument('--node_type', help='node_type', required=False)

    args = my_parser.parse_args()
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    is_infra = False
    if args.node_type is not None:
        is_infra = args.node_type == 'I' or args.node_type == "i"
    if not is_infra:
        print("Vehicle-", args.vehicle_id)
        latitude = float(args.latitude)
        longitude = float(args.longitude)
        get_vehicle = Vehicle(int(args.vehicle_id), host, int(args.listen_port), int(args.sending_port), latitude, longitude)
        get_vehicle.deploy()
    else:
        print("isInfra-", args.vehicle_id)
        get_infra = Infra(int(args.vehicle_id), host, int(args.listen_port), int(args.sending_port))
        get_infra.deploy()


if __name__ == '__main__':
    main()
