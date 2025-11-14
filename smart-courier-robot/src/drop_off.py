from utils.brick import BP, TouchSensor, Motor, wait_ready_sensors, SensorError
import time
import math

MOTOR_POLL_DELAY = 0.05

SQUARE_LENGTH = 0.5     # (meters) Side length of square in
WHEEL_RADIUS = 0.022    # (meters) Radius of one wheel
AXLE_LENGTH = 0.077      # (meters) Distance between wheel contact with ground

DIST_TO_DEG = 180/(math.pi*WHEEL_RADIUS)
ORIENT_TO_DEG = AXLE_LENGTH / WHEEL_RADIUS # Convert whole robot rotation to wheel rotation

FMD_SPEED = 150         # (deg per sec) Moving forward speed
TRN_SPEED = 180         # (deg per sec) Turning a corner speed

LEFT_MOTOR = Motor("A") # Left motor in Port A
RIGHT_MOTOR = Motor("D") # Right motor in Port D
POWER_LIMIT = 80        # Power limit = 80%
SPEED_LIMIT = 720       # Speed limit = 720dps

#PORTS
T_SENSOR = TouchSensor(1) # colour Sensor in Port S1 CHANGE WHEN IN LAB
LEFT_MOTOR = Motor("A")   # Left motor in Port A
RIGHT_MOTOR = Motor("D")  # Right motor in Port D
SERVO_MOTOR = Motor("B")  # Right motor in Port D
SWEEP_ARM = Motor("C")

def wait_for_motor(motor: Motor):
    while math.isclose(motor.get_speed(), 0):
        time.sleep(MOTOR_POLL_DELAY)
    while not math.isclose(motor.get_speed(), 0):
        time.sleep(MOTOR_POLL_DELAY)


def init_motor(motor: Motor):
    """Function to initialize a motor"""
    try:
        motor.reset_encoder() # Reset encoder to 0 value
        motor.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set power and speed limits
        motor.set_power(0) # Stop the motor as well
    except IOError as error:
        print(error)


def move_dist_fwd(distance, speed): # meters, dps
    """Function to move forward by user-specified distance and speed"""
    try:
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed) # Set speeds of motors
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)
        LEFT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG)) # Rotate wheels
        RIGHT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))

        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)


def rotate(angle, speed):
    try:
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)   # Set speed
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)   # Set speed
        LEFT_MOTOR.set_position_relative(int(angle * ORIENT_TO_DEG))   # Rotate L wheel +ve
        RIGHT_MOTOR.set_position_relative(int(-angle * ORIENT_TO_DEG)) # Rotate R wheel -ve
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)

def drop_package():
    try:
        #SERVO_MOTOR.set_limits(POWER_LIMIT, 20)
        SERVO_MOTOR.set_position_relative(90)
        wait_for_motor(SERVO_MOTOR)
        print("dropped off")
    except IOError as error:
        print(error)


try:
    wait_ready_sensors() # Wait for sensors to initialize
    print('Dropping off')
    #init_motor(LEFT_MOTOR) # Initialize L Motor
    #init_motor(RIGHT_MOTOR) # Initialize R Motor
    
    drop_package()

except KeyboardInterrupt: # Abort program using ^C (Ctrl+C)
    BP.reset_all()
