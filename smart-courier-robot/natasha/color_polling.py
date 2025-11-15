import brickpi3
from utils.brick import wait_ready_sensors, EV3ColorSensor, BP, TouchSensor, Motor, SensorError
import time
import globals

BP = brickpi3.BrickPi3()
color = EV3ColorSensor(3)
SWEEP_ARM = Motor("C")
wait_ready_sensors()


try:
    while globals.SWEEPS < 6:
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