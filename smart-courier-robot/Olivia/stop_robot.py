from utils.brick import BP, SensorError, TouchSensor
import time
import os
import globals


T_SENSOR = TouchSensor(2)
SENSOR_POLL_SLEEP = 0.05

def stop_robot():
    try:
        if T_SENSOR.is_pressed():  # Press touch sensor to stop robot
            BP.reset_all()
            os._exit(0)
            exit()
        time.sleep(SENSOR_POLL_SLEEP)
    except SensorError as error:
        print(error)

def stop_robot_thread():
    while True:
        stop_robot()