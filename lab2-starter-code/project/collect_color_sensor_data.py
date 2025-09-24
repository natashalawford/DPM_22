#!/usr/bin/env python3

"""
This test is used to collect data from the color sensor.
It must be run on the robot.
"""

# Add your imports here, if any
import os
from utils.brick import BP, EV3ColorSensor, wait_ready_sensors, TouchSensor


COLOR_SENSOR_DATA_FILE = "../data_analysis/color_sensor.csv"

# complete this based on your hardware setup
COLOR = EV3ColorSensor(3)
TOUCH = TouchSensor(1)

wait_ready_sensors(True) # Input True to see what the robot is trying to initialize! False to be silent.


def collect_color_sensor_data():
    "Collect color sensor data."
    
    
#     if not os.path.exists(COLOR_SENSOR_DATA_FILE):
#         print(f"Error: {COLOR_SENSOR_DATA_FILE} does not exist.")
#         sys.exit(1)

    with open(COLOR_SENSOR_DATA_FILE, "a") as color_file:
        
        prev_pressed = False
        
        try:
            while True:
                pressed = TOUCH.is_pressed()

                if pressed and not prev_pressed:
                    r, g, b = COLOR.get_rgb()

                    print(f"RGB: {r}, {g}, {b}")
                    color_file.write(f"{r}, {g}, {b}\n")
                    color_file.flush()

                prev_pressed = pressed
    
        except BaseException:
            print("Stopping collection.")
            return



if __name__ == "__main__":
    collect_color_sensor_data()