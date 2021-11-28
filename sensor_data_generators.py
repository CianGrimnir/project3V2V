#Author: Omkar
# generate sensor values
from random import randint
import time
from datetime import datetime


class PressureSensor:

    def __init__(self):
        self.INITIAL_PRESSURE = self.SET_INITIAL_PRESSURE()
        self.PRESSURE=0

    def SET_INITIAL_PRESSURE(self):
        randvalue = randint(0, 100)

        if(randvalue <= 97): # 97% chance of correct tyre pressure
            #print("1")
            INITIAL_VALUE = randint(30,35)      # Normal tyre pressure
        elif randvalue == 98:
            #print("2")
            INITIAL_VALUE = randint(25,30)      # 1% chance Below Normal tyre pressure
        elif randvalue == 99:
            #print("3")
            INITIAL_VALUE = randint(35,40)      # 1% chance Above normal tyre pressure
        else:
            #print("4")
            INITIAL_VALUE = randint(15,25)      # 1% chance flat tyre

        return INITIAL_VALUE

    def GET_DATA(self):
        randvalue2 = randint(0,10000)
        if randvalue2 <= 9998:  # return same as initial value
            self.PRESSURE = self.INITIAL_PRESSURE
        elif randvalue2 == 9999: # decrease in tyre pressure
            self.PRESSURE = self.INITIAL_PRESSURE - 1
            self.INITIAL_PRESSURE = self.INITIAL_PRESSURE - 1
        else:
            self.PRESSURE = self.INITIAL_PRESSURE + 1
            self.INITIAL_PRESSURE = self.INITIAL_PRESSURE + 1

        return ['TP',self.PRESSURE]

class SpeedSensor:

    def __init__(self):
        self.INITIAL_SPEED = randint(40,80)
        self.SPEED=0
        self.TICKS=0
        self.FLAG='DEFAULT'

    def SET_INITIAL_SPEED(self):
        self.INITIAL_SPEED = randint(40,80)
        return self.INITIAL_SPEED

    def GET_DATA(self,param_FLAG='DEFAULT'):

        if(self.TICKS == 0):
            self.FLAG=param_FLAG

        randvalue2 = randint(0,100)

        if randvalue2 <= 33 and self.FLAG=='DEFAULT':  # return same as initial value
            self.SPEED = self.INITIAL_SPEED

        elif ((randvalue2 > 33 and randvalue2 <= 66 and self.FLAG=='DEFAULT') or self.FLAG=='INCREASE'): # increase in speed
            if(self.INITIAL_SPEED < 200):
                self.INITIAL_SPEED=self.INITIAL_SPEED+randint(1,10)
            self.SPEED = self.INITIAL_SPEED

            if(self.FLAG == 'INCREASE'):
                self.TICKS+=1
                if(self.TICKS == 5):
                    self.TICKS=0
                    self.FLAG='DEFAULT'

        else:
            self.INITIAL_SPEED=self.INITIAL_SPEED-randint(1,10)

            if(self.INITIAL_SPEED<0):
                self.INITIAL_SPEED=0

            self.SPEED = self.INITIAL_SPEED


            if(self.FLAG == 'DECREASE'):
                self.TICKS+=1
                if(self.TICKS == 5):
                    self.TICKS=0
                    self.FLAG='DEFAULT'
        # print("-----------")
        # print("TICKS: ",self.TICKS," FLAG: ",self.FLAG)
        # print("-----------")
        return ['SPD',self.SPEED]



class LightSensor():

    def __init__(self):
        self.LIGHT="DEFAULT" #Does not matter, will change depending on time
        self.d1 = datetime(2020, 5, 13, 8, 00, 00)
        self.d2 = datetime(2020, 5, 13, 17, 00, 00)

    def GET_DATA(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # print("Current Time =", current_time)

        if(now.time() >= self.d1.time() and now.time() <= self.d2.time()):
            self.LIGHT='HIGH'
        else:
            self.LIGHT='LOW'

        return ['LT',self.LIGHT]


class FuelSensor():

    def __init__(self):
        self.INITIAL_FUEL = randint(40,80)  # % fuel left in tank
        self.FUEL=self.INITIAL_FUEL
        self.TICKS=0

    def GET_DATA(self):

        if( self.TICKS % 50 == 0):
            self.FUEL -= 1

        self.TICKS+=1

        return ['FLG',self.FUEL]

    def REFILL_FUEL(self,REFILL_PERCENT):
        self.FUEL += REFILL_PERCENT

        if(self.FUEL >100):
            self.FUEL = 100


class ProximitySensor:
    def __init__(self):
        self.PROXIMITY_LEFT = False
        self.PROXIMITY_RIGHT = False
        self.PROXIMITY_FRONT = False
        self.PROXIMITY_BEHIND = False

    def GET_DATA(self, FLAG='LEFT'):
        randvalue = randint(0,100)
        randvalue1 = randint(0,100)
        randvalue2 = randint(0,100)
        randvalue3 = randint(0,100)

        # Flip the output pobability 33%
        if(randvalue>=67):
            self.PROXIMITY_LEFT = (not self.PROXIMITY_LEFT)

        if(randvalue1>=67):
            self.PROXIMITY_RIGHT = (not self.PROXIMITY_RIGHT)

        if(randvalue2>=67):
            self.PROXIMITY_FRONT = (not self.PROXIMITY_FRONT)

        if(randvalue3>=67):
            self.PROXIMITY_BEHIND = (not self.PROXIMITY_BEHIND)


        return ['PRX',self.PROXIMITY_LEFT,self.PROXIMITY_RIGHT,self.PROXIMITY_FRONT,self.PROXIMITY_BEHIND]
        # if(FLAG=='LEFT'):
        #     return ['PRX',self.PROXIMITY_LEFT]
        # if(FLAG=='RIGHT'):
        #     return ['PRX',self.PROXIMITY_RIGHT]
        # if(FLAG=='FRONT'):
        #     return ['PRX',self.PROXIMITY_FRONT]
        # if(FLAG=='BEHIND'):
        #     return ['PRX',self.PROXIMITY_BEHIND]

class BrakeSensor:

    def __init__(self):
        self.BRAKE_APPLIED = False
        self.TICKS = 0

    def ApplyBrake(self):
        self.BRAKE_APPLIED = True
        self.TICKS = 0

    def GET_DATA(self):

        if(self.BRAKE_APPLIED== True and self.TICKS == 4 ):
            self.BRAKE_APPLIED = False
            self.TICKS=0

        self.TICKS += 1

        return ['BRK',self.BRAKE_APPLIED]

class HeartRateSensor:

    def __init__(self):
        self.INITIAL_HEART_RATE = randint(60,100)

    def GET_DATA(self):

        randvalue2 = randint(0,100)
        if randvalue2 <= 33:  # return same as initial value
            self.HEART_RATE = self.INITIAL_HEART_RATE
        elif randvalue2 > 33 and randvalue2 <=66: # decrease in heart rate
            self.HEART_RATE = self.INITIAL_HEART_RATE - 1
            self.INITIAL_HEART_RATE = self.INITIAL_HEART_RATE - 1
        else:                                       # increase in heart rate
            self.HEART_RATE = self.INITIAL_HEART_RATE + 1
            self.INITIAL_HEART_RATE = self.INITIAL_HEART_RATE + 1

        return ['HRS',self.HEART_RATE]


class GPSSensor:

    def __init__(self):
        self.INITIAL_LAT = 53.3498
        self.INITIAL_LONG = 6.2603

        self.INITIAL_LAT = self.INITIAL_LAT + randint(0,10)/10
        self.INITIAL_LONG = self.INITIAL_LONG + randint(0,10)/10

    def GET_DATA(self):

        self.INITIAL_LAT += randint(0,10)/1000
        self.INITIAL_LONG += randint(0,10)/1000

        return ['GPS', "("+str(self.INITIAL_LAT)+","+str(self.INITIAL_LONG)+")"]

# Changing the name to sensors, as it makes more sense
class Sensors:

    #making the sensors instance variables as it 
    #gives as control over the sensor objects usings the object of Sensors
    def getSensors(self):
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
        sensorObjects.append(self.s1)
        sensorObjects.append(self.l1)
        sensorObjects.append(self.f1)
        sensorObjects.append(self.px1)
        sensorObjects.append(self.b1)
        sensorObjects.append(self.hrs)
        sensorObjects.append(self.gps)


        return sensorObjects

def GET_SENSOR_DATA():

# For Testing
    S = Sensors()
    Sobj = S.GetSensors()

    for _ in range(100):
        time.sleep(1)
        for s in Sobj:
            print(s.GET_DATA())



#GET_SENSOR_DATA()

