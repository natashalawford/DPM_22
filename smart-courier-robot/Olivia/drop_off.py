from utils.brick import BP, TouchSensor, Motor, wait_ready_sensors, SensorError, EV3ColorSensor
from utils.sound import Sound
import time
import math
import globals
from threading import Thread
import runpy
import os

MOTOR_POLL_DELAY = 0.05

SQUARE_LENGTH = 0.5     # (meters) Side length of square in
WHEEL_RADIUS = 0.022    # (meters) Radius of one wheel
AXLE_LENGTH = 0.077      # (meters) Distance between wheel contact with ground

DIST_TO_DEG = 180/(math.pi*WHEEL_RADIUS)
ORIENT_TO_DEG = AXLE_LENGTH / WHEEL_RADIUS # Convert whole robot rotation to wheel rotation

FMD_SPEED = 150         # (deg per sec) Moving forward speed
TRN_SPEED = 180         # (deg per sec) Turning a corner speed

POWER_LIMIT = 80        # Power limit = 80%
SPEED_LIMIT = 720       # Speed limit = 720dps

#PORTS
T_SENSOR = TouchSensor(1) # colour Sensor in Port S1 CHANGE WHEN IN LAB
LEFT_MOTOR = Motor("A")   # Left motor in Port A
RIGHT_MOTOR = Motor("D")  # Right motor in Port D
DROP_MOTOR = Motor("B")  # Right motor in Port D
SWEEP_ARM = Motor("C")

# SWEEPING ARM CONSTANTS
FWD_SWEEP_DIST = 0.02 # distance robot moves forward between each sweep (m)
SWEEP_SPEED = 50 # Speed of sweeping arm
SWEEPING_ANGLE = 110 # Angle sweeping arm moves each sweep (deg)
FWD_SWEEP_SPEED = 120 # Speed the robot is moving between each sweep


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
        print("fwd")
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed) # Set speeds of motors
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)
        LEFT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG)) # Rotate wheels
        RIGHT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))

        wait_for_motor(RIGHT_MOTOR)
        #wait_for_motor(LEFT_MOTOR)
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
        DROP_MOTOR.set_limits(POWER_LIMIT, 70)
        DROP_MOTOR.set_position_relative(90)
        wait_for_motor(DROP_MOTOR)
        print("dropped off")
        # Play success sound :
        Sound(duration=0.6, volume=80, pitch="C5").play().wait_done()
    except IOError as error:
        print(error)

def sweep(direction):
    try:
        print("sweeping")
        SWEEP_ARM.set_limits(POWER_LIMIT, SWEEP_SPEED)
        SWEEP_ARM.set_position_relative(SWEEPING_ANGLE * direction)
        wait_for_motor(SWEEP_ARM)
    except IOError as error:
        print(error)


try:
    wait_ready_sensors() # Wait for sensors to initialize
    #init_motor(LEFT_MOTOR) # Initialize L Motor
    #init_motor(RIGHT_MOTOR) # Initialize R Motor
    init_motor(DROP_MOTOR)

    
    # turn 90 DEG into office
    rotate(90, 180)
    print('Turning into office')
    SWEEP_ARM.set_limits(POWER_LIMIT, SWEEP_SPEED)
    #Move arm slightly to fit into office
    SWEEP_ARM.set_position_relative(32)
    wait_for_motor(SWEEP_ARM)



    # Start the existing color_polling.py script in a daemon thread
    # It runs its own loop and updates globals.COLOR.
    color_script = os.path.join(os.path.dirname(__file__), "color_polling.py")
    color_thread = Thread(target=lambda: runpy.run_path(color_script), daemon=True)
    color_thread.start()
    direction = 1
    while globals.SWEEPS < 10 and globals.COLOR != "Green":
        #sweep, mv fwd, add 1 to sweep
        move_dist_fwd(FWD_SWEEP_DIST , FWD_SWEEP_SPEED)
        time.sleep(0.1)
        sweep(direction)
        globals.SWEEPS += 1
        direction = direction * (-1) # switch direction of sweeping arm
        time.sleep(0.1)

    # Drop off package if green was detected
    if globals.COLOR == "Green":
        drop_package()
        globals.PACKAGES -= 1

    # Back out of office based on how many sweeps were completed:
    move_dist_fwd( (-FWD_SWEEP_DIST)*globals.SWEEPS, 150)

    # Reset SWEEPS and COLOR for next drop off:
    globals.SWEEPS = 0
    globals.COLOR = ""

    # Rotate back out *MORE LOGIC TO BE IMPLEMENTED HERE BASED ON
    # WHERE TO ROBOT IS AND IF IT NEEDS TO GO BACK TO MAIL ROOM
    rotate(-90, 180)
    # Move arm back to 90 deg
    SWEEP_ARM.set_position_relative(-32)

except KeyboardInterrupt: # Abort program using ^C (Ctrl+C)
    BP.reset_all()
