# Author: Omkar & Azin

from random import randint
import time
from datetime import datetime


# Azin
class SensorControls:
    """
    Class to hold the control variables across
    multiple sensors.
    """
    __instance = None
    FLAG = 'DEFAULT'
    BRAKE_LOCK = False
    BRAKE_APPLIED = False

    @staticmethod
    def getInstance():
        """
        To get the singleton instance of SensorControls.

        Returns:
            [SensorControls]: an instance of SensorControls class
        """
        if SensorControls.__instance is None:
            SensorControls.__instance = SensorControls()
        return SensorControls.__instance


# Azin


class PressureSensor:
    """
    Class for pressure sensor.
    """

    def __init__(self):
        """
            * Constructor for pressure sensor.
            * Initialises the initial values of the sensor
        """
        self.INITIAL_PRESSURE = self.SET_INITIAL_PRESSURE()
        self.PRESSURE = 0

    def SET_INITIAL_PRESSURE(self):
        """
        Sets the initial value for the senor.

        Returns:
            [Integer]: returns the initial value of the sensor.
        """
        randvalue = randint(0, 100)

        if randvalue <= 97:  # 97% chance of correct tyre pressure
            # print("1")
            INITIAL_VALUE = randint(30, 35)  # Normal tyre pressure
        elif randvalue == 98:
            # print("2")
            INITIAL_VALUE = randint(25, 30)  # 1% chance Below Normal tyre pressure
        elif randvalue == 99:
            # print("3")
            INITIAL_VALUE = randint(35, 40)  # 1% chance Above normal tyre pressure
        else:
            # print("4")
            INITIAL_VALUE = randint(15, 25)  # 1% chance flat tyre

        return INITIAL_VALUE

    def GET_DATA(self):
        """
        To get the sensor readings.

        Returns:
            [List]: Returns a list with the sensor type and senor value.
        """
        randvalue2 = randint(0, 10000)
        if randvalue2 <= 9998:  # return same as initial value
            self.PRESSURE = self.INITIAL_PRESSURE
        elif randvalue2 == 9999:  # decrease in tyre pressure
            self.PRESSURE = self.INITIAL_PRESSURE - 1
            self.INITIAL_PRESSURE = self.INITIAL_PRESSURE - 1
        else:
            self.PRESSURE = self.INITIAL_PRESSURE + 1
            self.INITIAL_PRESSURE = self.INITIAL_PRESSURE + 1

        return ['TP', self.PRESSURE]


class SpeedSensor:
    """
    Class for Odometer readings. 
    """
    def __init__(self):
        """
        Constructor for the SpeedSensor class
        """
        self.INITIAL_SPEED = randint(40, 80)
        self.SPEED = 0
        self.TICKS = 0

    def SET_INITIAL_SPEED(self):
        """
        Sets the initial sensor speed and returns the value.

        Returns:
            [Integer]: initial sensor reading
        """
        self.INITIAL_SPEED = randint(40, 80)
        return self.INITIAL_SPEED

    def GET_DATA(self):
        """Method to get the sensor reading.

        Returns:
            [List]: Returns a list with sensor type and the sensor readings. 
        """
        if self.TICKS == 0:
            # Azin
            self.FLAG = SensorControls.getInstance().FLAG

        randvalue2 = randint(0, 100)

        # Azin
        if SensorControls.getInstance().BRAKE_APPLIED:
            self.FLAG = 'DECREASE'

        if randvalue2 <= 33 and self.FLAG == 'DEFAULT':  # return same as initial value
            self.SPEED = self.INITIAL_SPEED

        elif (33 < randvalue2 <= 66 and self.FLAG == 'DEFAULT') or self.FLAG == 'INCREASE':  # increase in speed
            if self.INITIAL_SPEED < 200:
                self.INITIAL_SPEED = self.INITIAL_SPEED + randint(1, 10)
            self.SPEED = self.INITIAL_SPEED

            if self.FLAG == 'INCREASE':
                self.TICKS += 1
                if self.TICKS == 5:
                    self.TICKS = 0
                    self.FLAG = 'DEFAULT'

        else:
            self.INITIAL_SPEED = self.INITIAL_SPEED - randint(1, 10)

            if self.INITIAL_SPEED < 0:
                self.INITIAL_SPEED = 0

            self.SPEED = self.INITIAL_SPEED

            if self.FLAG == 'DECREASE':
                self.TICKS += 1
                if self.TICKS == 5:
                    self.TICKS = 0
                    self.FLAG = 'DEFAULT'
        # print("-----------")
        # print("TICKS: ",self.TICKS," FLAG: ",self.FLAG)
        # print("-----------")
        return ['SPD', self.SPEED]


class LightSensor():
    """Class for LightSensor
    """
    def __init__(self):
        """
        Constructor for Light sensor. Senses the indesity of visible lights.
        """
        self.LIGHT = "DEFAULT"  # Does not matter, will change depending on time
        self.d1 = datetime(2020, 5, 13, 8, 00, 00)
        self.d2 = datetime(2020, 5, 13, 17, 00, 00)

    def GET_DATA(self):
        """Gets the readings from LightSensor.

        Returns:
            [List]: Returns a list of with the sensor type and sensor readings.
        """
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # print("Current Time =", current_time)

        if self.d1.time() <= now.time() <= self.d2.time():
            self.LIGHT = 'HIGH'
        else:
            self.LIGHT = 'LOW'

        return ['LT', self.LIGHT]


class FuelSensor:
    """Class for Fuel sensor and its associated methods.
    """

    def __init__(self):
        """Constructor for Fuel Sensor
        """
        self.INITIAL_FUEL = randint(40, 80)  # % fuel left in tank
        self.FUEL = self.INITIAL_FUEL
        self.TICKS = 0

    def GET_DATA(self):
        """Get the fuel level on the vehicle fuel tank.

        Returns:
            [List]: Returns a list with the sensor type and the sensor readings. 
        """
        if self.TICKS % 50 == 0:
            self.FUEL -= 1

        self.TICKS += 1

        return ['FLG', self.FUEL]

    def REFILL_FUEL(self, REFILL_PERCENT):
        self.FUEL += REFILL_PERCENT

        if self.FUEL > 100:
            self.FUEL = 100


class ProximitySensor:
    """Class for the Proximity sensor, which detects proximity variations
    """
    def __init__(self):
        """Constructor to the proximity class
        """
        self.PROXIMITY_LEFT = False
        self.PROXIMITY_RIGHT = False
        self.PROXIMITY_FRONT = False
        self.PROXIMITY_BEHIND = False

    def GET_DATA(self, FLAG='LEFT'):
        """
        To detect proximity variations.

        Args:
            FLAG (str, optional): Takes sensor selector as argument. Defaults to 'LEFT'.

        Returns:
            [List]: Returns a list with sensor type and sensor readings.
        """
        randvalue = randint(0, 100)
        randvalue1 = randint(0, 100)
        randvalue2 = randint(0, 100)
        randvalue3 = randint(0, 100)

        # Flip the output pobability 33%
        if randvalue >= 67:
            self.PROXIMITY_LEFT = (not self.PROXIMITY_LEFT)

        if randvalue1 >= 67:
            self.PROXIMITY_RIGHT = (not self.PROXIMITY_RIGHT)

        if randvalue2 >= 67:
            self.PROXIMITY_FRONT = (not self.PROXIMITY_FRONT)

        if randvalue3 >= 67:
            self.PROXIMITY_BEHIND = (not self.PROXIMITY_BEHIND)

        return ['PRX', self.PROXIMITY_LEFT, self.PROXIMITY_RIGHT, self.PROXIMITY_FRONT, self.PROXIMITY_BEHIND]
        # if(FLAG=='LEFT'):
        #     return ['PRX',self.PROXIMITY_LEFT]
        # if(FLAG=='RIGHT'):
        #     return ['PRX',self.PROXIMITY_RIGHT]
        # if(FLAG=='FRONT'):
        #     return ['PRX',self.PROXIMITY_FRONT]
        # if(FLAG=='BEHIND'):
        #     return ['PRX',self.PROXIMITY_BEHIND]


class BrakeSensor:
    """Class for the brake sensor. 
    """
    def __init__(self):
        """Constructor for brake sensor.
        """
        self.TICKS = 0

    def ApplyBrake(self):
        """To explicitly apply the brakes.
        """
        SensorControls.getInstance().BRAKE_APPLIED = True
        self.TICKS = 0

    def GET_DATA(self):
        """Get the readings from brake sensor.

        Returns:
            [List]: Returns a list with the sensor type and sensor readings.
        """
        # Azin
        if self.TICKS == 4:
            if not SensorControls.getInstance().BRAKE_LOCK:
                SensorControls.getInstance().BRAKE_APPLIED = not SensorControls.getInstance().BRAKE_APPLIED
            self.TICKS = 0

        self.TICKS += 1

        return ['BRK', SensorControls.getInstance().BRAKE_APPLIED]


class HeartRateSensor:
    """
    Class for heartrate monitor sensor.
    """
    def __init__(self):
        """constructor for heart rate monitor
        """
        self.INITIAL_HEART_RATE = self.SET_INITIAL_HEART_RATE()

    def SET_INITIAL_HEART_RATE(self):
        """To set the initial heart rate. 

        Returns:
            [List]: Returns sensor readings.
        """
        randvalue = randint(0, 100)

        if randvalue <= 97:  # 97% chance of normal heart rate
            # print("1")
            INITIAL_VALUE = randint(60, 100)  # Normal tyre pressure
        elif randvalue == 98:
            # print("2")
            INITIAL_VALUE = randint(40, 60)  # 1% chance Below Normal
        elif randvalue == 99:
            # print("3")
            INITIAL_VALUE = randint(100, 120)  # 1% chance Above normal
        else:
            # print("4")
            INITIAL_VALUE = randint(0, 40)  # 1% chance very low

        return INITIAL_VALUE

    def GET_DATA(self):
        """Method to get the real time heart rate of the passenger.

        Returns:
            [List]: Returns the sensor type and sensor reading as a list
        """
        randvalue2 = randint(0, 100)
        if randvalue2 <= 33:  # return same as initial value
            self.HEART_RATE = self.INITIAL_HEART_RATE
        elif 33 < randvalue2 <= 66:  # decrease in heart rate
            self.HEART_RATE = self.INITIAL_HEART_RATE - 1
            self.INITIAL_HEART_RATE = self.INITIAL_HEART_RATE - 1
        else:  # increase in heart rate
            self.HEART_RATE = self.INITIAL_HEART_RATE + 1
            self.INITIAL_HEART_RATE = self.INITIAL_HEART_RATE + 1

        return ['HRS', self.HEART_RATE]


class GPSSensor:
    """Class for GPS sensor
    """
    def __init__(self):
        """Constructor for GPS sensor.
        """
        self.INITIAL_LAT = 53.3498
        self.INITIAL_LONG = 6.2603

        self.INITIAL_LAT = self.INITIAL_LAT + randint(0, 10) / 10
        self.INITIAL_LONG = self.INITIAL_LONG + randint(0, 10) / 10

    def GET_DATA(self):
        """Method to get the readings from the sensor.

        Returns:
            [List]: Returns a list of the sensor type and the readings from the sensor.
        """
        self.INITIAL_LAT += randint(0, 10) / 1000
        self.INITIAL_LONG += randint(0, 10) / 1000

        return ['GPS', "(" + str(self.INITIAL_LAT) + "," + str(self.INITIAL_LONG) + ")"]


class Sensors:

    """Master class to hold all the sensors of the vehicle.
    """
    def getSensors(self):
        """Method to initialise all the sensor of the vehicle.

        Returns:
            [List]: List of sensor objects
        """
        self.p1 = PressureSensor()
        self.s1 = SpeedSensor()
        self.l1 = LightSensor()
        self.f1 = FuelSensor()
        self.px1 = ProximitySensor()
        self.b1 = BrakeSensor()
        self.hrs = HeartRateSensor()
        self.gps = GPSSensor()

        sensorObjects = []
        sensorObjects.append(self.p1)
        # sensorObjects.append(self.s1)
        sensorObjects.append(self.l1)
        sensorObjects.append(self.f1)
        sensorObjects.append(self.px1)
        sensorObjects.append(self.b1)
        sensorObjects.append(self.hrs)
        sensorObjects.append(self.gps)

        return sensorObjects

    def setSpeedSensor(self, value):
        """Method to explicitly control the speed sensor.

        Args:
            value (str): Control value
        """
        self.s1.FLAG = value


    # Azin
    def applyBrake(self, value):
        """Method to forcefully apply brakes

        Args:
            value (str): Control value
        """
        if value == 'A':
            SensorControls.getInstance().BRAKE_APPLIED = True
            SensorControls.getInstance().BRAKE_LOCK = True
        else:
            SensorControls.getInstance().BRAKE_APPLIED = False
            SensorControls.getInstance().BRAKE_LOCK = False


