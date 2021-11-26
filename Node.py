"""
Control layer.
constantly looks for sensor data,
According to the sensor data, then raise proper alerts

sensors used :
1. Speed gauge 
2. Tyre pressure
3. Steering wheel change
4. Proximity/ radar
5. GPS
6. Heartrate monitor
7. Brake sensor
8. Fuel gauge

if tyre pressure is low :
    then alert all peers --- I may cause an accident
if proximity sensor/radar data :
    then alert the neighbours --- you are too close to me
if speed increases :
    then alert the neighbours --- I am speeding up.
if speed decreases :
    then alert the neighbours --- I am slowing down
if steering wheel change : 
    then alert the neighbours ---- I am changing my direction
if GPS down or unavailable :
    then alert the neighbours
if Heartrate :
    then alert the neighbours --- Passenger in danger
if brake applied :
    then alert the neighbours --- Sudden brake
if .....

"""
# Azin
import logging
import argparse
from os import posix_fallocate
import time
import threading
import random

logging.basicConfig(level=logging.INFO)
args_parser = argparse.ArgumentParser()
args_parser.add_argument('--nodeid', help='a number', required=True)
node_id = args_parser.parse_args().nodeid

def get_data_from_speed():
    return ['SPD', 1]
def get_data_from_tyre_pressure():
    return ['TP', 0]
def get_data_from_lane_change_sensor():
    return ['SWL', 0]
def get_data_from_proximity():
    return ['PRX', 0]
def get_data_from_GPS():
    return ['GPS', 0]
def get_data_from_BP_sensor() :
    return ['BPS', 0]
def get_data_from_brake():
    return ['BRK', 0]
def get_data_from_fuel_gauge() :
    return ['FLG', 0]



sensor_data_generator = [get_data_from_speed, get_data_from_tyre_pressure, get_data_from_lane_change_sensor, get_data_from_proximity,
    get_data_from_GPS, get_data_from_BP_sensor, get_data_from_brake, get_data_from_fuel_gauge]

def send_broadcast(data) :
    logging.info("Broadcasting")


class vehicle:
    def __init__( self ):
        self.lane = random.choices([0,1])
        self.speed = 0
        self.tyrePressure = 0
        self.proximity = 0
        self.BP = 0
        self.GPS = 0
        self.fuel = 0
        self.brake = 0
        self.position = 0


def runVehicle(vehicle: vehicle) :
    while True :
        for func in sensor_data_generator :
            data = func()
            if data[0] == 'SPD' :
                vehicle.position = vehicle.position + data[1]
                vehicle.speed = data[1]
                print( "position = " + str(v.position))
                if data[1] > 60 :
                    logging.info("["+ node_id+ "] Broadcasting overspeeding alert")
                    send_broadcast("["+ node_id +"] is overspeeding")
            elif data[0] == 'TP' :
                vehicle.tyrePressure = + data[1]
                if data[1] > 100 :
                    logging.info("["+ node_id +"] Broadcasting tyre pressure low alert")
                    send_broadcast("["+ node_id +"] Typre pressure is low")
            elif data[0] == 'SWL' : 
                if data[1] != vehicle.lane :
                    vehicle.lane = data[1]
                    logging.info("["+ node_id +"] Broadcasting direction changing alert")
                    send_broadcast("["+ node_id +"] changing direction")
            elif data[0] == 'PRX' :
                vehicle.proximity = data[1]
                if data[1] > 100 :
                    logging.info("["+ node_id +"] Broadcasting proximity alert")
                    send_broadcast("["+ node_id +"] proximity alert")
            elif data[0] == 'GPS' :
                vehicle.GPS = data[1]
                if data[1] < 100 :
                    logging.info("["+ node_id+ "] Broadcasting low signal alert")
                    send_broadcast("["+ node_id +"] low GPS signal alert")
            elif data[0] == 'BPS' : 
                vehicle.BP = data[1]
                if data[1] < 100 :
                    logging.info("["+ node_id +"] Broadcasting passenger in danger alert")
                    send_broadcast("["+ node_id +"] low GPS signal alert")
            elif data[0] == 'BRK' : 
                vehicle.brake = data[1]
                if data[1] < 100 :
                    logging.info("["+ node_id +"] Broadcasting stopping alert")
                    send_broadcast("["+ node_id +"] stopping alert")
            elif data[0] == 'FLG' : 
                vehicle.fuel = data[1]
                if data[1] < 100 :
                    logging.info("["+ node_id +"] Broadcasting low fuel alert")
                    send_broadcast("["+ node_id +"] low fuel alert")
            
        time.sleep(1)

v = vehicle()

runner = threading.Thread(target=runVehicle, args=( v, ))

runner.start()
