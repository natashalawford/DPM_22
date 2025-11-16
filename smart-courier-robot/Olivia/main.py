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

# LINEAR MOTION
DIST_TO_DEG = 360 / (2 * math.pi * WHEEL_RADIUS)  # deg per meter
ROOM_FORWARD_DIST = 0.25  # m forward after detecting door

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

def stop_robot():
    try:
        if T_SENSOR.is_pressed(): # Press touch sensor to stop robot
            print("Button pressed")
            BP.reset_all()
            exit()
        time.sleep(SENSOR_POLL_SLEEP) # Use sensor polling interval here
    except SensorError as error:
        print(error) # On exception or error, print error code
def clamp(v, lo, hi):
        return max(lo, min(hi, v))
def path_correction(dist):
    # Use a proportional controller to steer the robot so it holds a
    # target distance from the wall on the right. The mapping used is:
    #  error = WALL_DST - dist
    #  left_speed  = base - Kp * error
    #  right_speed = base + Kp * error
    # This results in left>right (turn right) when dist > WALL_DST
    # and right>left (turn left) when dist < WALL_DST.
    

    try:
        # basic safety checks
        if dist is None:
            return
        if T_SENSOR.is_pressed():
            print("Button pressed")
            BP.reset_all()
            exit()

        # controller params (tune these on the robot)
        Kp = 8.0           # proportional gain (dps per unit distance)
        DEADBAND = 0.2     # meters (or same units as your sensor)

        error = WALL_DST - dist
        # small errors -> keep straight to avoid hunting
        if abs(error) <= DEADBAND:
            LEFT_MOTOR.set_dps(FORWARD_SPEED)
            RIGHT_MOTOR.set_dps(FORWARD_SPEED)
            return

        # compute wheel speeds
        left_speed = FORWARD_SPEED - (Kp * error)
        right_speed = FORWARD_SPEED + (Kp * error)

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

    except Exception as e:
        # If reading fails, don't change motor state
        print(f"Ultrasonic read error: {e}")
        return
    

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
        


try:
    wait_ready_sensors() # Wait for sensors to initialize
    LEFT_MOTOR.set_dps(FORWARD_SPEED)
    RIGHT_MOTOR.set_dps(FORWARD_SPEED)
    while True:
        stop_robot()
        # read ultrasonic sensor and call controller every cycle
        
        dist = us.get_value()
       
        # controller params (tune these on the robot)
        Kp = 10.0         # proportional gain (dps per unit distance)
        DEADBAND_WALL = 0.55
        DEADBAND = 0.3
        DEADBAND_ROOM = 0.1 # meters (or same units as your sensor)

        error = WALL_DST - dist
        print(dist)
        print(error)

        current_color = detect_color()
        room_entered = False

        if current_color == "Red": 
            print("Red detected. Not entering room")
            LAST_COLOR = current_color
            break
        if (not room_entered) and current_color in ("Yellow", "Orange"): 
            if LAST_COLOR not in ("Yellow", "Orange"): 
                room_entered = True 
                print(f"Room detected. Total doors entered: {DOOR_COUNT + 1}") 
                DOOR_COUNT += 1 
                #Right now in seconds, @natashalawford change this for distance!
                forward_deg = int(ROOM_FORWARD_DIST * DIST_TO_DEG)
                print("Continuing forward for {ROOM_FORWARD_DIST} m (~{forward_deg} deg).")
                
                LEFT_MOTOR.set_dps(FORWARD_SPEED)
                RIGHT_MOTOR.set_dps(FORWARD_SPEED)
                LEFT_MOTOR.set_position_relative(forward_deg)
                RIGHT_MOTOR.set_position_relative(forward_deg)
                
                while True: 
                    stop_robot()
                    current_color = detect_color() 
                    if current_color == "Red": 
                        print("Red detected. Not entering room")
                        room_entered = False
                        break
                    if math.isclose(LEFT_MOTOR.get_speed(), 0, abs_tol=1.0) and \
                        math.isclose(RIGHT_MOTOR.get_speed(), 0, abs_tol=1.0):    
                        LEFT_MOTOR.set_dps(0) 
                        RIGHT_MOTOR.set_dps(0)
        # small errors -> keep straight to avoid hunting
        if abs(error) <= DEADBAND:
            LEFT_MOTOR.set_dps(FORWARD_SPEED)
            RIGHT_MOTOR.set_dps(FORWARD_SPEED)
            print("go straight")
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

        # call the path correction controller (handles deadband internally)
        #path_correction(dist)
        time.sleep(SENSOR_POLL_SLEEP)
        

except KeyboardInterrupt: # Allows program to be stopped on keyboard interrupt
    BP.reset_all()
