from utils.brick import BP, EV3UltrasonicSensor, TouchSensor, Motor, wait_ready_sensors, SensorError, EV3ColorSensor
import time
import math

#DRIVING
FORWARD_SPEED = 100        # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05  # Polling rate = 50 msec

#TURNING
WHEEL_RADIUS = 0.022
AXEL_LENGTH = 0.078
ORIENTTODEG = AXEL_LENGTH / WHEEL_RADIUS
POWER_LIMIT = 80
MOTOR_POLL_DELAY = 0.05
TURNING = "neutral"

# State for detecting Yellow -> Green transitions
LAST_COLOR = None
DOOR_COUNT = 0
WALL_DST = 7.0

us = EV3UltrasonicSensor(1) # Ultrasonic sensor in Port 1

#PORTS
T_SENSOR = TouchSensor(2) # Touch Sensor in Port S2
LEFT_MOTOR = Motor("A")   # Left motor in Port A
RIGHT_MOTOR = Motor("D")  # Right motor in Port D
color = EV3ColorSensor(3)
COLOR_SENSOR_DATA_FILE="./color_data.csv"

def clamp(v, lo, hi):
        return max(lo, min(hi, v))

def stop_robot():
    try:
        if T_SENSOR.is_pressed(): # Press touch sensor to stop robot
            print("Button pressed")
            BP.reset_all()
            exit()
        time.sleep(SENSOR_POLL_SLEEP) # Use sensor polling interval here
    except SensorError as error:
        print(error) # On exception or error, print error code
    



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
    LEFT_MOTOR.set_dps(FORWARD_SPEED)
    RIGHT_MOTOR.set_dps(FORWARD_SPEED)
    LAST_COLOR = "black"
    
    def is_color_sustained(target, samples=3, delay=SENSOR_POLL_SLEEP):
        """Return True if `target` is read in the majority of `samples` calls to detect_color()."""
        matches = 0
        for _ in range(samples):
            c = color.get_color_name()
            if c == target.lower():
                matches += 1
            time.sleep(delay)
        return matches >= (samples // 2) + 1

    # small state variable to avoid rotating repeatedly while still on the same green patch
    just_rotated = False

    while True:
        stop_robot()
        # use the more robust RGB-based detector (detect_color) and normalize to lowercase
        detected_color = color.get_color_name()
        print(f"Detected (normalized): {detected_color}")
        dist = us.get_value()
       
        # controller params (tune these on the robot)
        Kp = 20.0         # proportional gain (dps per unit distance)
        DEADBAND_WALL = 0.55
        DEADBAND = 0.3
        DEADBAND_ROOM = 0.1 # meters (or same units as your sensor)

        error = WALL_DST - dist
        print(dist)
        print(error)
            # small errors -> keep straight to avoid hunting
        if abs(error) <= DEADBAND:
            LEFT_MOTOR.set_dps(FORWARD_SPEED)
            RIGHT_MOTOR.set_dps(FORWARD_SPEED)
            print("go straigt")
        if error < -DEADBAND_ROOM:
            print("go right")

                # compute wheel speeds
            left_speed = FORWARD_SPEED + (Kp * error)
            right_speed = FORWARD_SPEED - (Kp * error)

                # keep speeds within safe range
            max_speed = POWER_LIMIT
            left_speed = clamp(left_speed, -max_speed, max_speed)
            right_speed = clamp(right_speed, -max_speed, max_speed)

                # set limits (power limit, dps limit)
            LEFT_MOTOR.set_limits(POWER_LIMIT, abs(FORWARD_SPEED))
            RIGHT_MOTOR.set_limits(POWER_LIMIT, abs(FORWARD_SPEED))

            LEFT_MOTOR.set_dps(left_speed)
            RIGHT_MOTOR.set_dps(right_speed)
            LEFT_MOTOR.set_dps(FORWARD_SPEED)
            RIGHT_MOTOR.set_dps(FORWARD_SPEED)
        elif error > DEADBAND_WALL:
            print("go left")
                    

                # compute wheel speeds
            left_speed = FORWARD_SPEED + (Kp * error)
            right_speed = FORWARD_SPEED - (Kp * error)

                # keep speeds within safe range
            max_speed = POWER_LIMIT
            left_speed = clamp(left_speed, -max_speed, max_speed)
            right_speed = clamp(right_speed, -max_speed, max_speed)

                # set limits (power limit, dps limit)
            LEFT_MOTOR.set_limits(POWER_LIMIT, abs(FORWARD_SPEED))
            RIGHT_MOTOR.set_limits(POWER_LIMIT, abs(FORWARD_SPEED))

            LEFT_MOTOR.set_dps(left_speed)
            RIGHT_MOTOR.set_dps(right_speed)


        if dist is None:
            # sensor failed this cycle; don't change motors and keep polling
            time.sleep(SENSOR_POLL_SLEEP)
            continue
        # Count door when we see yellow transitioning from a different color
        if detected_color == "yellow" and LAST_COLOR != "yellow":
            DOOR_COUNT += 1
            print(f"Door count: {DOOR_COUNT}")
            LAST_COLOR = "yellow"
            just_rotated = False
        elif detected_color != "yellow":
            LAST_COLOR = detected_color

        # Only rotate if we reliably detect green and are at the target door count
        if detected_color == "green" and (DOOR_COUNT == 2 or DOOR_COUNT == 4) and not just_rotated:
            # require sustained green reading to avoid false positives
            if is_color_sustained("green", samples=50):
                print("At destination, stopping and rotating")
                rotate(90, FORWARD_SPEED)
                # after rotation, restore forward drive and continue moving forward
                LEFT_MOTOR.set_dps(FORWARD_SPEED)
                RIGHT_MOTOR.set_dps(FORWARD_SPEED)
                # small pause to let motors settle and to move off the patch
                time.sleep(0.2)
                just_rotated = True
                # reset LAST_COLOR so future transitions are detected
                LAST_COLOR = "unknown"
                continue
    
except KeyboardInterrupt: # Allows program to be stopped on keyboard interrupt
    BP.reset_all()