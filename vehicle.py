import control as ctrl 
import argparse
import socket
import threading
import time
from flask import Flask, render_template


app = Flask(__name__)
@app.route('/vehicle/sensor_controls/speed/<string:value>')
def speedControl(value):
    vehicle = Vehicle.getInstance()
    if value == "D" :
        vehicle.sensorMaster.setSpeedSensor("DECREASE")
    elif value == "I" :
        vehicle.sensorMaster.setSpeedSensor("INCREASE")
    else :
        vehicle.sensorMaster.setSpeedSensor("DEFAULT")
    return "Signal generated"

@app.route('/vehicle/sensor_controls/brake/<string:value>')
def brakeControl(value):
    vehicle = Vehicle.getInstance()
    vehicle.sensorMaster.applyBrake(value)
    return "Signal generated"

class Vehicle( ctrl.VehicleControls) :
    __instance = None

    @staticmethod 
    def getInstance():
      return Vehicle.__instance

    def __init__(self, vehicle_id, host_address, listening_port, sending_port):
        super().__init__(vehicle_id, host_address, listening_port, sending_port)
        Vehicle.__instance = self

    def deploy(self):
        return super().deploy()

class Infra( ctrl.InfraControls) :
    def __init__(self, vehicle_id, host_address, listening_port, sending_port):
        super().__init__(vehicle_id, host_address, listening_port, sending_port)
    
    def deploy(self):
        return super().deploy()
    
def Main() :
    my_parser = argparse.ArgumentParser(description='command to execute the ./server script')
    my_parser.add_argument('--listen_port', help='listening_port', required=True)
    my_parser.add_argument('--sending_port', help='sending_port', required=True)
    my_parser.add_argument('--vehicle_id', help='vehicle_id', required=True)
    my_parser.add_argument('--node_type', help='node_type', required=False)
    my_parser.add_argument('--api_port', help='api_port', required=False)
    
    args = my_parser.parse_args()
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    is_infra = False
    if args.node_type != None : 
        is_infra = args.node_type == 'I' or args.node_type == "i"
    if not is_infra:
        print("Vehicle-", args.vehicle_id)
        get_vehicle = Vehicle( int(args.vehicle_id), host, int(args.listen_port), int(args.sending_port))
        get_vehicle.deploy()
    else :
        print("isInfra-",args.vehicle_id)
        get_infra = Infra( int(args.vehicle_id), host, int(args.listen_port), int(args.sending_port))
        get_infra.deploy()
    app.run(host='localhost', port=int(args.api_port))
    
if __name__ == '__main__':
    Main()
    