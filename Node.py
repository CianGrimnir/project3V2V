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
        self.sensors = sensor_data_generator #[""" list of sensor objects"""]

    def runVehicle( self) :
        while True :
            for sensor in self.sensors :
                #data = sensor.get_data()
                data = sensor()
                if data[0] == 'SPD' :
                    self.process_speed_data(data)
                elif data[0] == 'TP' :
                    self.process_tyre_pressure_data(data)
                elif data[0] == 'SWL' : 
                    self.process_lane_switch_data(data)
                elif data[0] == 'PRX' :
                    self.process_proximity_data(data)
                elif data[0] == 'GPS' :
                    self.process_gps_data(data)
                elif data[0] == 'BPS' : 
                    self.process_BP_data(data)
                elif data[0] == 'BRK' : 
                    self.process_brake_sensor_data(data)
                elif data[0] == 'FLG' : 
                    self.process_fuel_guage_data(data)
            time.sleep(1)

    def process_fuel_guage_data(self, data):
        self.fuel = data[1]
        if data[1] < 100 :
            logging.info("["+ node_id +"] Broadcasting low fuel alert")
            send_broadcast("["+ node_id +"] low fuel alert")

    def process_brake_sensor_data(self, data):
        self.brake = data[1]
        if data[1] < 100 :
            logging.info("["+ node_id +"] Broadcasting stopping alert")
            send_broadcast("["+ node_id +"] stopping alert")

    def process_BP_data(self, data):
        self.BP = data[1]
        if data[1] < 100 :
            logging.info("["+ node_id +"] Broadcasting passenger in danger alert")
            send_broadcast("["+ node_id +"] No BP alert")

    def process_gps_data(self, data):
        self.GPS = data[1]
        if data[1] < 100 :
            logging.info("["+ node_id+ "] Broadcasting low signal alert")
            send_broadcast("["+ node_id +"] low GPS signal alert")

    def process_proximity_data(self, data):
        self.proximity = data[1]
        if data[1] > 100 :
            logging.info("["+ node_id +"] Broadcasting proximity alert")
            send_broadcast("["+ node_id +"] proximity alert")

    def process_lane_switch_data(self, data):
        if data[1] != self.lane :
            self.lane = data[1]
            logging.info("["+ node_id +"] Broadcasting direction changing alert")
            send_broadcast("["+ node_id +"] changing direction")

    def process_tyre_pressure_data(self, data):
        self.tyrePressure = + data[1]
        if data[1] > 100 :
            logging.info("["+ node_id +"] Broadcasting tyre pressure low alert")
            send_broadcast("["+ node_id +"] Typre pressure is low")

    def process_speed_data(self, data):
        self.position = self.position + data[1]
        self.speed = data[1]
        print( "position = " + str(v.position))
        if data[1] > 60 :
            logging.info("["+ node_id+ "] Broadcasting overspeeding alert")
            send_broadcast("["+ node_id +"] is overspeeding")
        

v = vehicle()

runner = threading.Thread(target=v.runVehicle, args=( ))

runner.start()
