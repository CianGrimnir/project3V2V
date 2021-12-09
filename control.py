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
import time
import threading
import random
import sensor_data_generators as sdg
import broadcast_system as bs
from random import randint
import json

logging.basicConfig(level=logging.INFO)
args_parser = argparse.ArgumentParser()
args_parser.add_argument('--nodeid', help='a number', required=False)

FUEL_LIMIT = 80


class InfraControls(bs.BroadcastSystem):
    def __init__(self, vehicle_id, host_address, listening_port, sending_port, latitude, longitude):
        super().__init__(vehicle_id, host_address, listening_port, sending_port, (latitude, longitude))
        self.sensors = """ list of sensors for infra--->  weather, """
        self.nodeId = vehicle_id

    def runInfra(self):
        threading.Thread(target=self.periodic_updater).start()

    # Whenever a new data is received on this node,
    # the control comes here.
    def information_processor(self, data):
        """Wat to do with the received data ? """
        print("On infra--->[" + data + "]")
        data = json.loads(data)
        if data["senorId"] == "LT":
            logging.info("Received LOW LIGHTS alert from vehicle[" + data["vehicleId"] + "]")
            self.send_information({"infraNodeId": str(self.nodeId), "control": "Turn on lights"})
            logging.info(" Successfully sent lights control signal to vehicle[" + data["vehicleId"] + "]")
        elif data["senorId"] == "FLG":
            logging.info("Received LOW FUEL alert from vehicle[" + data["vehicleId"] + "]")
            self.send_information({"infraNodeId": str(self.nodeId), "destination": "Gas Station 10021", "dataType": "GPS", "lat": str(
                53.3498 - randint(0, 10)) + '", "lon" : "' + str(6.2603 - randint(0, 10))})
            logging.info(" Successfully sent GAS STATION info to vehicle[" + data["vehicleId"] + "]")
        elif data["senorId"] == "HRS" and ( data["senorReading"] < 60 or data["senorReading"] > 100) :
            self.takeActionOnDanger(data)

    # Thread to push periodic updates to all connected nodes
    def periodic_updater(self):
        while True:
            predictions = ['rainy', 'sunny', 'windy', 'overcast']
            self.send_information({"infraNodeId": str(self.nodeId), "alert": "Weather alert", "senorId": "WTR", "senorReading": random.choices(predictions)[0]})
            time.sleep(10)
    def takeActionOnDanger(self, data) :
        logging.info("Received PASSENGER IN DANGER alert from vehicle[" + data["vehicleId"] + "]")
        self.findNearestHospital(data)
        logging.info(" Successfully sent Hospital location info to vehicle[" + data["vehicleId"] + "]")
    
    def findNearestHospital(self, data) :
        self.send_information({"infraNodeId": str(self.nodeId), "destination": "Hospital X14S9AS", "dataType": "GPS", "lat": str(
                55.3584 - randint(0, 10)) + '", "lon" : "' + str(5.2953 - randint(0, 10))})
    

    def deploy(self):
        super().deploy(self.information_processor)
        self.runInfra()


class VehicleControls(bs.BroadcastSystem):
    def __init__(self, vehicle_id, host_address, listening_port, sending_port, latitude, longitude):
        super().__init__(vehicle_id, host_address, listening_port, sending_port, (latitude, longitude))
        self.vehicle_id = vehicle_id
        self.lane = random.choices([0, 1])
        self.speed = 0
        self.tyrePressure = 0
        self.proximity = 0
        self.BP = 0
        self.GPS = 0
        self.fuel = 0
        self.brake = 0
        self.position = 0
        self.sensorMaster = sdg.Sensors()
        self.sensors = self.sensorMaster.getSensors()  # [""" list of sensor objects"""]

    def runVehicle(self):
        while True:
            for sensor in self.sensors:
                data = sensor.GET_DATA()
                # data = sensor()
                if data[0] == 'SPD':
                    self.process_speed_data(data)
                elif data[0] == 'TP':
                    self.process_tyre_pressure_data(data)
                elif data[0] == 'LT':
                    self.process_light_sensor_data(data)
                elif data[0] == 'PRX':
                    self.process_proximity_data(data)
                elif data[0] == 'GPS':
                    self.process_gps_data(data)
                elif data[0] == 'HRS':
                    self.process_HRS_data(data)
                elif data[0] == 'BRK':
                    self.process_brake_sensor_data(data)
                elif data[0] == 'FLG':
                    self.process_fuel_guage_data(data)
            time.sleep(1)

    def process_fuel_guage_data(self, data):
        self.fuel = data[1]
        if data[1] < FUEL_LIMIT:
            logging.info(f'[{self.vehicle_id}] Broadcasting low fuel alert')
            self.send_information({"vehicleId": str(self.vehicle_id), "alert" : "Low fuel", "senorId" : "FLG", "senorReading" : str(data[1])})

    def process_brake_sensor_data(self, data):
        self.brake = data[1]
        if data[1]:
            logging.info(f'[{self.vehicle_id}] Broadcasting stopping alert')
            self.send_information({"vehicleId": str(self.vehicle_id), "alert" : "Brake applied", "senorId" : "BRK", "senorReading" : str(data[1])})

    def process_HRS_data(self, data):
        self.BP = data[1]
        if data[1] < 60 or data[1] > 100:
            location = self.sensorMaster.gps.GET_DATA()
            logging.info(f'[{self.vehicle_id}] Broadcasting passenger in danger alert')
            self.send_information({"vehicleId": str(self.vehicle_id), "alert" : "Low or high heart rate", "senorId" : "HRS", "senorReading" : str(data[1]), "location" : location[1] })

    def process_gps_data(self, data):
        self.GPS = data[1]
        logging.info(f'[{self.vehicle_id}] Broadcasting GPS signal')
        self.send_information({"vehicleId": str(self.vehicle_id), "alert" : "GPS co-ordinates", "senorId" : "GPS", "senorReading" : str(data[1])})

    def process_proximity_data(self, data):
        self.proximity = data[1]
        if data[1] == True or data[2] == True or data[3] == True or data[4] == True:
            logging.info(f'[{self.vehicle_id}] Broadcasting proximity alert')
            self.send_information({"vehicleId": str(self.vehicle_id), "alert" : "Proximity alert", "senorId" : "PRX", "senorReading" : str(data[1])})

    def process_light_sensor_data(self, data):
        if data[1] == "LOW":
            logging.info(f'[ {self.vehicle_id}] Broadcasting low lights alert')
            print(f"sensor LOW {str(data[1])} {type(data[1])}")
            self.send_information({"vehicleId": str(self.vehicle_id), "alert": "Low lights alert", "senorId": "LT", "senorReading": str(data[1])})

    def process_tyre_pressure_data(self, data):
        self.tyrePressure = + data[1]
        if data[1] < 30 or data[1] > 35:
            logging.info(f'[ {self.vehicle_id}] Broadcasting tyre pressure low alert')
            self.send_information({"vehicleId": str(self.vehicle_id), "alert": "Low or high tyre pressure alert", "senorId": "TP", "senorReading": str(data[1])})

    def process_speed_data(self, data):
        self.position = self.position + data[1]
        self.speed = data[1]
        print("position = " + str(self.position) + ", Speed = " + str(data[1]))
        if data[1] > 80:
            logging.info(f'[{self.vehicle_id}] Broadcasting over speeding alert')
            self.send_information({"vehicleId": str(self.vehicle_id), "alert": "Over speeding alert", "senorId": "SPD", "senorReading": str(data[1])})

    def get_vehicle_runner_thread(self):
        return threading.Thread(target=self.runVehicle, args=( ))

    def information_processor(self):
        pass

    def stimulate_vehicle_run(self):
        while True:
            data = self.sensorMaster.s1.GET_DATA()
            self.process_speed_data(data)
            time.sleep(2)

    def deploy(self):
        super().deploy(self.information_listener)
        self.get_vehicle_runner_thread().start()
        threading.Thread(target=self.stimulate_vehicle_run, args=( )).start()

# runner.start()

# v = VehicleControls(vehicle_id)

# runner = v.get_vehicle_runner_thread()

# runner.start()
