import brickpi3
from utils.brick import wait_ready_sensors, EV3ColorSensor, BP, TouchSensor, Motor, SensorError
import time
import globals

BP = brickpi3.BrickPi3()
color = EV3ColorSensor(3)
SWEEP_ARM = Motor("C")
wait_ready_sensors()


try:
    while globals.SWEEPS < 10:
        # @ RACH I used red for testing dropped off - we need to use better color detection
        # If I could get help with this, that'd be great
        # I'm currently using color.get_color_names() from utils that returns
        # A string with the name of the color detected
        # Just edit it so that your function is here instead of
        # color.get_color_name(), that returns the names of the colors
        # Add any imports to this file or csv files to my folder as needed
        # That would be amazing! Thanks!
        name = color.get_color_name()
        print("Color name:", name)
        key = name.lower()

        if key == "green":
            globals.COLOR = "Green"
            SWEEP_ARM.set_power(0)
            break

        time.sleep(0.2)

except KeyboardInterrupt:
    BP.reset_all()