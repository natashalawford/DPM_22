import brickpi3
import time
from utils.brick import TouchSensor, wait_ready_sensors, reset_brick


# Config parameters
# ------------------------------
POWER_LIMIT = 80
MOTOR_SPEED = -275                 # Speed for Design 1 (Lucy, you may change this)
MOTOR_PORT = brickpi3.BrickPi3.PORT_A
TOUCH_PORT = 1
# ------------------------------

# Initialize hardware
BP = brickpi3.BrickPi3()
TOUCH_SENSOR = TouchSensor(TOUCH_PORT)

wait_ready_sensors(True)
print("Touch sensor in port 1 to toggle drumming ON/OFF.")

# Motor setup
BP.offset_motor_encoder(MOTOR_PORT, BP.get_motor_encoder(MOTOR_PORT))
BP.set_motor_limits(MOTOR_PORT, POWER_LIMIT, MOTOR_SPEED)
BP.set_motor_power(MOTOR_PORT, 0)

# State variables
motor_running = False
previous_pressed = False

try:
    while True:
        pressed = TOUCH_SENSOR.is_pressed()

        # Detect if pressed now but wasn't pressed before
        if pressed and not previous_pressed:
            motor_running = not motor_running  # Swap the state
            if motor_running:
                print("Drumming started")
                BP.set_motor_dps(MOTOR_PORT, MOTOR_SPEED)
            else:
                print("Drumming stopped")
                BP.set_motor_power(MOTOR_PORT, 0)

        # Remember previous sensor state for next loop
        previous_pressed = pressed
        time.sleep(0.05)

except KeyboardInterrupt:
    BP.reset_all()
