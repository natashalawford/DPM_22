from utils.brick import BP, EV3UltrasonicSensor, TouchSensor, Motor, wait_ready_sensors, SensorError, EV3ColorSensor
import time
import math

#DRIVING
FORWARD_SPEED = 140        # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05  # Polling rate = 50 msec

#TURNING
WHEEL_RADIUS = 0.022
AXEL_LENGTH = 0.078
ORIENTTODEG = AXEL_LENGTH / WHEEL_RADIUS
POWER_LIMIT = 150
MOTOR_POLL_DELAY = 0.05
TURNING = "neutral"

# State for detecting Yellow -> Green transitions
LAST_COLOR = None
DOOR_COUNT = 0
color = EV3ColorSensor(3)

#Path following distance from wall
WALL_DST = 5.7
us = EV3UltrasonicSensor(1) # Ultrasonic sensor in Port 1
Kp = 20.0         
DEADBAND = 0.3

#PORTS
T_SENSOR = TouchSensor(2) # Touch Sensor in Port S2
LEFT_MOTOR = Motor("D")   # Left motor in Port D
RIGHT_MOTOR = Motor("A")  # Right motor in Port A


def stop_robot():
    try:
        if T_SENSOR.is_pressed(): # Press touch sensor to stop robot
            print("Button pressed")
            BP.reset_all()
            exit()
        time.sleep(SENSOR_POLL_SLEEP) # Use sensor polling interval here
    except SensorError as error:
        print(error) # On exception or error, print error code
          

def detect_color():
    """Detect color based on RGB value ranges"""
    try:
        r, g, b = color.get_rgb()
        print(f"RGB: {r}, {g}, {b}")
        
        # Define color ranges (R_min, R_max, G_min, G_max, B_min, B_max)
        color_ranges = {
            "Black": (15, 40, 11, 33, 8, 19),
            "Green": (90, 102, 120, 128, 16, 22),
            "Red": (122, 132, 11, 18, 7, 13),
            "Orange": (145, 205, 56, 77, 9, 16),
            "Yellow": (142, 242, 101, 165, 13, 24)
        }
        
        detected_color = "Unknown"
        
        # Check each color range in order of specificity
        if (color_ranges["Black"][0] <= r <= color_ranges["Black"][1] and
            color_ranges["Black"][2] <= g <= color_ranges["Black"][3] and
            color_ranges["Black"][4] <= b <= color_ranges["Black"][5]):
            detected_color = "Black"
            
        elif (color_ranges["Green"][0] <= r <= color_ranges["Green"][1] and
              color_ranges["Green"][2] <= g <= color_ranges["Green"][3] and
              color_ranges["Green"][4] <= b <= color_ranges["Green"][5]):
            detected_color = "Green"
            
        elif (color_ranges["Red"][0] <= r <= color_ranges["Red"][1] and
              color_ranges["Red"][2] <= g <= color_ranges["Red"][3] and
              color_ranges["Red"][4] <= b <= color_ranges["Red"][5]):
            detected_color = "Red"
            
        elif (color_ranges["Orange"][0] <= r <= color_ranges["Orange"][1] and
              color_ranges["Orange"][2] <= g <= color_ranges["Orange"][3] and
              color_ranges["Orange"][4] <= b <= color_ranges["Orange"][5]):
            detected_color = "Orange"
            
        elif (color_ranges["Yellow"][0] <= r <= color_ranges["Yellow"][1] and
              color_ranges["Yellow"][2] <= g <= color_ranges["Yellow"][3] and
              color_ranges["Yellow"][4] <= b <= color_ranges["Yellow"][5]):
            detected_color = "Yellow"
        
        print(f"Detected color: {detected_color}")
        return detected_color
        
    except SensorError as error:
        print(f"Color sensor error: {error}")
        return "Unknown"
    except BaseException as error:
        print(f"Unexpected error in detect_color: {error}")
        return "Unknown"



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
        
def clamp(v, lo, hi):
        return max(lo, min(hi, v))

def is_color_sustained(target, samples=3, delay=SENSOR_POLL_SLEEP):
    """Return True if `target` is read in the majority of `samples`."""
    matches = 0
    for _ in range(samples):
        c = color.get_color_name()
        if c == target.lower():
            matches += 1
        time.sleep(delay)
    return matches >= (samples // 2) + 1

try:
    wait_ready_sensors() # Wait for sensors to initialize
    LEFT_MOTOR.set_dps(FORWARD_SPEED)
    RIGHT_MOTOR.set_dps(FORWARD_SPEED)
    just_rotated = False
    while True:
        stop_robot()
        
        # read ultrasonic sensor and call controller every cycle
        dist = us.get_value()
        error = WALL_DST - dist
        print(f"dist: {dist}")
        print(f"error: {error}")

        # small errors -> keep straight to avoid hunting
        if abs(error) <= DEADBAND:
            LEFT_MOTOR.set_dps(FORWARD_SPEED)
            RIGHT_MOTOR.set_dps(FORWARD_SPEED)
            print("go straight")
            
        if error < -DEADBAND:
            print("go right")
            # compute wheel speeds
            left_speed = FORWARD_SPEED - (Kp * error)
            right_speed = FORWARD_SPEED + (Kp * error)
            
            # keep speeds within safe range
            left_speed = clamp(left_speed, -POWER_LIMIT, POWER_LIMIT)
            print(f"left speed: {left_speed}")
            right_speed = clamp(right_speed, -POWER_LIMIT, POWER_LIMIT)
            print(f"right speed: {right_speed}")
    
            LEFT_MOTOR.set_dps(left_speed)
            RIGHT_MOTOR.set_dps(right_speed)
            
        elif error > DEADBAND:
            print("go left")

            # compute wheel speeds
            left_speed = FORWARD_SPEED - (Kp * error)
            right_speed = FORWARD_SPEED + (Kp * error)

            # keep speeds within safe range
       
            left_speed = clamp(left_speed, -POWER_LIMIT, POWER_LIMIT)
            print(f"left speed: {left_speed}")
            right_speed = clamp(right_speed, -POWER_LIMIT, POWER_LIMIT)
            print(f"right speed: {right_speed}")

            LEFT_MOTOR.set_dps(left_speed)
            RIGHT_MOTOR.set_dps(right_speed)


        if dist is None:
            # sensor failed this cycle; don't change motors and keep polling
            time.sleep(SENSOR_POLL_SLEEP)
            continue

        time.sleep(SENSOR_POLL_SLEEP)
        
        
        # color detection and door counting
        detected_color = color.get_color_name()
        print(f"Detected color: {detected_color}")
        # Count door when we see yellow transitioning from a different color
        if detected_color == "yellow" and LAST_COLOR != "yellow":
            DOOR_COUNT += 1
            print(f"Door count: {DOOR_COUNT}")
            LAST_COLOR = "yellow"
            just_rotated = False
        elif detected_color != "yellow":
            LAST_COLOR = detected_color

        # Only rotate if we reliably detect green and are at the target door count
        if detected_color == "green" and (DOOR_COUNT == 2 or DOOR_COUNT == 3) and not just_rotated:
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
