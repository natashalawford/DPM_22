import brickpi3
from utils.brick import wait_ready_sensors, EV3ColorSensor
import time
import globals

BP = brickpi3.BrickPi3()
color = EV3ColorSensor(3)
wait_ready_sensors()


try:
    while globals.SWEEPS < 6:
        name = color.get_color_name()
        print("Color name:", name)

        key = name.lower()

        if key == "green":
            globals.COLOR = "Green"
            break

        time.sleep(0.2)

except KeyboardInterrupt:
    BP.reset_all()