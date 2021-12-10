# Authors: Azin, Rakesh & Omkar  

import control as ctrl
import argparse
import socket
import threading
import time
from flask import Flask, render_template
import logging

logging.basicConfig(format='%(asctime)-15s  %(message)s', level=logging.INFO)

app = Flask(__name__)


@app.route('/vehicle/sensor_controls/speed/<string:value>')
def speedControl(value):
    """API to forcefully control the speed sensor.

    Args:
        value (str): Control string

    Returns:
        [Str]: A sucess message 
    """
    vehicle = Vehicle.getInstance()
    if value == "D":
        vehicle.sensorMaster.setSpeedSensor("DECREASE")
    elif value == "I":
        vehicle.sensorMaster.setSpeedSensor("INCREASE")
    else:
        vehicle.sensorMaster.setSpeedSensor("DEFAULT")
    return "Signal generated"


@app.route('/vehicle/sensor_controls/brake/<string:value>')
def brakeControl(value):
    """API to forcefully control the brake sensor.

    Args:
        value (str): Control string

    Returns:
        [Str]: A sucess message 
    """
    vehicle = Vehicle.getInstance()
    vehicle.sensorMaster.applyBrake(value)
    return "Signal generated"

@app.route('/vehicle/sensor_controls/hrs/<string:value>')
def heartRateControl(value):
    """API to forcefully control the heart rate sensor.

    Args:
        value (str): Control string

    Returns:
        [Str]: A sucess message 
    """
    vehicle = Vehicle.getInstance()
    vehicle.sensorMaster.controlHeartRate(value)
    return "Signal generated"

@app.route('/vehicle/sensor_controls/fuel/<string:value>')
def fuelLevelControl(value):
    """API to forcefully control the heart rate sensor.

    Args:
        value (str): Control string

    Returns:
        [Str]: A sucess message 
    """
    vehicle = Vehicle.getInstance()
    vehicle.sensorMaster.controlFuelLevel(value)
    return "Signal generated"

class Vehicle(ctrl.VehicleControls):
    """
    Class for the vehicle node extending the control layer for 
    the vehicle
    """
    __instance = None

    @staticmethod
    def getInstance():
        return Vehicle.__instance

    def __init__(self, vehicle_id, host_address, listening_port, sending_port, latitude, longitude):
        super().__init__(vehicle_id, host_address, listening_port, sending_port, latitude, longitude)
        Vehicle.__instance = self

    def deploy(self):
        return super().deploy()


class Infra(ctrl.InfraControls):
    """
    Class for the Infra node extending the control layer for 
    the Infra
    """
    def __init__(self, vehicle_id, host_address, listening_port, sending_port, latitude, longitude):
        super().__init__(vehicle_id, host_address, listening_port, sending_port, latitude, longitude)

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
    my_parser.add_argument('--api_port', help='api_port', required=False)

    args = my_parser.parse_args()
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    is_infra = False
    latitude = float(args.latitude)
    longitude = float(args.longitude)
    if args.node_type is not None:
        is_infra = args.node_type == 'I' or args.node_type == "i"
    if not is_infra:
        logging.info("<-----### -{Vehicle-" + args.vehicle_id + "}- ###----->")
        get_vehicle = Vehicle(int(args.vehicle_id), host, int(args.listen_port), int(args.sending_port), latitude, longitude)
        get_vehicle.deploy()
    else:
        logging.info("<-----### -{Infra-" + args.vehicle_id + "}- ###----->")
        get_infra = Infra(int(args.vehicle_id), host, int(args.listen_port), int(args.sending_port), latitude, longitude)
        get_infra.deploy()
    app.run(host='localhost', port=int(args.api_port))


if __name__ == '__main__':
    main()
