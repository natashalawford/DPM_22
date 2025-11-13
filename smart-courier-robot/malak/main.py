from utils.brick import BP, EV3UltrasonicSensor, TouchSensor, Motor, wait_ready_sensors, SensorError, EV3ColorSensor
import time
import math

#DRIVING
FORWARD_SPEED = 20        # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05  # Polling rate = 50 msec

#TURNING
WHEEL_RADIUS = 0.022
AXEL_LENGTH = 0.078
ORIENTTODEG = AXEL_LENGTH / WHEEL_RADIUS
POWER_LIMIT = 80
MOTOR_POLL_DELAY = 0.05

#PORTS
T_SENSOR = TouchSensor(2) # Touch Sensor in Port S2
LEFT_MOTOR = Motor("A")   # Left motor in Port A
RIGHT_MOTOR = Motor("D")  # Right motor in Port D
color = EV3ColorSensor(3)
COLOR_SENSOR_DATA_FILE="./color_data.csv"

# State for detecting Yellow -> Green transitions
LAST_COLOR = None
DOOR_COUNT = 0

us = EV3UltrasonicSensor(1) # Ultrasonic sensor in Port 1

def avoid_walls():
    """Ensure the robot drives straight forward while maintaining at least 10 cm
    distance from obstacles in front. This function is intended to be called
    frequently from the main loop; it will set motor powers to drive forward
    and perform a short backup+turn if an object is detected closer than 10 cm.
    """
    try:
        dist = us.get_value()
    except Exception as e:
        # If reading fails, don't change motor state
        print(f"Ultrasonic read error: {e}")
        return

    # If sensor returns None or invalid, do nothing
    if dist is None:
        return

    # If obstacle is too close, perform evasive action
    if dist < 10:
        print(f"avoid_walls: object too close ({dist} cm). Backing up and turning.")
        try:
         
            # stop and turn to avoid obstacle
            LEFT_MOTOR.set_power(0)
            RIGHT_MOTOR.set_power(0)
            time.sleep(0.05)

            # small rotation (45 degrees) to try a new direction
            rotate(45, 120)

            # resume forward motion
            LEFT_MOTOR.set_power(FORWARD_SPEED)
            RIGHT_MOTOR.set_power(FORWARD_SPEED)
        except Exception as e:
            print(f"avoid_walls error during evasive action: {e}")
    else:
        # nothing nearby: ensure we drive straight forward
        LEFT_MOTOR.set_power(FORWARD_SPEED)
        RIGHT_MOTOR.set_power(FORWARD_SPEED)

def detect_color():
    global LAST_COLOR, DOOR_COUNT
    name = color.get_color_name()
    print("Color name:", name)

    # Detect a transition from Yellow to Green (only when previous read was Yellow
    # and current read is Green). Increment a counter when that happens.
    if LAST_COLOR == "Yellow" and name == "Green":
        DOOR_COUNT += 1
        print(f"Detected Yellow->Green transition. Count={DOOR_COUNT}")
        # If we've seen exactly 2 or 3 such transitions, trigger a rotate
        if DOOR_COUNT in (2, 3):
            print("Count is 2 or 3 — calling rotate")
            try:
                rotate(90, 180)
            except Exception as e:
                print(f"rotate() raised an exception: {e}")

    # Update last seen color for next call
    LAST_COLOR = name
    # with open(COLOR_SENSOR_DATA_FILE, "a") as color_file:
    #     try:
    #         while True:
    #                 r, g, b = color.get_rgb()
    #                 print(f"RGB: {r}, {g}, {b}")
    #                 color_file.write(f"{r}, {g}, {b}\n")
    #                 color_file.flush()
    #     except BaseException:
    #         print("Stopping collection.")
    #         return



def wait_for_motor(motor: Motor):
    while math.isclose(motor.get_speed(), 0):
        time.sleep(MOTOR_POLL_DELAY)
    while not math.isclose(motor.get_speed(), 0):
        time.sleep(MOTOR_POLL_DELAY)
        
def rotate(angle, speed):
    try:
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)   # Set speed
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)   # Set speed
        LEFT_MOTOR.set_position_relative(int(angle * ORIENTTODEG))   # Rotate L wheel +ve
        RIGHT_MOTOR.set_position_relative(int(-angle * ORIENTTODEG)) # Rotate R wheel -ve
        wait_for_motor(RIGHT_MOTOR)
        print("i wanna rotate")
    except IOError as error:
        print(error)
        
try:
    wait_ready_sensors() # Wait for sensors to initialize
    
    LEFT_MOTOR.set_power(FORWARD_SPEED) # Start left motor
    RIGHT_MOTOR.set_power(FORWARD_SPEED) # Simultaneously start right motor
    print("motors set up and running")

    while True:
        try:
            avoid_walls()
            detect_color()
            if T_SENSOR.is_pressed(): # Press touch sensor to stop robot
                print("Button pressed")
                rotate(90, 180)
                BP.reset_all()
                exit()
            time.sleep(SENSOR_POLL_SLEEP) # Use sensor polling interval here
        except SensorError as error:
            print(error) # On exception or error, print error code

except KeyboardInterrupt: # Allows program to be stopped on keyboard interrupt
    BP.reset_all()
