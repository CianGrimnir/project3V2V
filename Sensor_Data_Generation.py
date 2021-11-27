# generate random integer values
from random import seed
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

class Sensor:
    def GetSensors(self):
        p1 = PressureSensor()
        s1 = SpeedSensor()
        l1 = LightSensor()
        f1 = FuelSensor()

        sensorObjects = []
        sensorObjects.append(p1)
        sensorObjects.append(s1)
        sensorObjects.append(l1)
        sensorObjects.append(f1)

        return sensorObjects

def GET_SENSOR_DATA():


    S = Sensor()
    Sobj = S.GetSensors()

    for s in Sobj:
        print(s.GET_DATA())



    # This is just for TESTING

    p1 = PressureSensor()
    s1 = SpeedSensor()
    l1 = LightSensor()
    f1 = FuelSensor()

    for _ in range(0,100):
        time.sleep(1)
        PRESSURE = p1.GET_DATA()

        if(_%20 ==0):
            SPEED = s1.GET_DATA('DECREASE')    #Trial for decrease
        else:
            SPEED = s1.GET_DATA('DEFAULT')

        LIGHT = l1.GET_DATA()

        FUEL = f1.GET_DATA()

        print("PRESSURE: "+str(PRESSURE[1]))
        print("SPEED: "+str(SPEED[1]))
        print("LIGHT: "+str(LIGHT[1]))
        print("FUEL: "+str(FUEL[1]))


GET_SENSOR_DATA()

