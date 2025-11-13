from utils.brick import BP, TouchSensor, Motor, wait_ready_sensors, SensorError
import time
import math

#DRIVING
BACKWARD_SPEED = 25       # speed constant = 25% power
FORWARD_SPEED = 30        # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05  # Polling rate = 50 msec
BACKWARD_ROTATION = -1440  # rotation amount to back up in DEG
IO_OFFICE_ROTATION = 1080  # rotation amount to enter office in DEG

#TURNING
WHEEL_RADIUS = 0.022
AXEL_LENGTH = 0.078
ORIENTTODEG = AXEL_LENGTH / WHEEL_RADIUS
POWER_LIMIT = 80
MOTOR_POLL_DELAY = 0.05

#PORTS
T_SENSOR = TouchSensor(1) # colour Sensor in Port S1 CHANGE WHEN IN LAB
LEFT_MOTOR = Motor("A")   # Left motor in Port A
RIGHT_MOTOR = Motor("D")  # Right motor in Port D

# USED FOR TURNING
def wait_for_motor(motor: Motor):
    while math.isclose(motor.get_speed(), 0):
        time.sleep(MOTOR_POLL_DELAY)
    while not math.isclose(motor.get_speed(), 0):
        time.sleep(MOTOR_POLL_DELAY)

# USED FOR TURNING        
def rotate(angle, speed):
    try:
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)   # Set speed
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)   # Set speed
        LEFT_MOTOR.set_position_relative(int(angle * ORIENTTODEG))   # Rotate L wheel +ve
        RIGHT_MOTOR.set_position_relative(int(-angle * ORIENTTODEG)) # Rotate R wheel -ve
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)
        


try:
    wait_ready_sensors() # Wait for sensors to initialize

    LEFT_MOTOR.set_limits(POWER_LIMIT, BACKWARD_SPEED)
    RIGHT_MOTOR.set_limits(POWER_LIMIT, BACKWARD_SPEED)
    LEFT_MOTOR.set_position_relative(BACKWARD_ROTATION) # Set distance to back up
    RIGHT_MOTOR.set_position_relative(BACKWARD_ROTATION) # Set distance to back up simultaneously
    print("robot backing up")

    # Now Turn 90 degrees facing the office
    rotate(90, 180)
    print("robot turned")
    
    # Move forward into the office
    LEFT_MOTOR.set_position_relative(IO_OFFICE_ROTATION) # Set distance to move forward
    RIGHT_MOTOR.set_position_relative(IO_OFFICE_ROTATION) # Set distance to move forward simultaneously
    print("robot moving into office")

except KeyboardInterrupt: # Allows program to be stopped on keyboard interrupt
    BP.reset_all()
