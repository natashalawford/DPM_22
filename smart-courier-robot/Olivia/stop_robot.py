from utils.brick import BP, SensorError
from globals import T_SENSOR
import time

SENSOR_POLL_SLEEP = 0.05

def stop_robot():
    try:
        if T_SENSOR.is_pressed():  # Press touch sensor to stop robot
            print("Button pressed")
            BP.reset_all()
            exit()
        time.sleep(SENSOR_POLL_SLEEP)
    except SensorError as error:
        print(error)

def stop_robot_thread():
    while True:
        stop_robot()