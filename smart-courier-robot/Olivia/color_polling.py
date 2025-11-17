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
        name = color.get_color_name()
        print("Color name:", name)
        key = name.lower()

        # Used red for testing dropped off - we need to use better color detection
        # If I could get help with this, that'd be great
        if key == "red":
            globals.COLOR = "Green"
            SWEEP_ARM.set_power(0)
            break

        time.sleep(0.2)

except KeyboardInterrupt:
    BP.reset_all()