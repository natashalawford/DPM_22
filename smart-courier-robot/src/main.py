from utils.brick import BP, TouchSensor, Motor, wait_ready_sensors, SensorError, EV3ColorSensor
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
    
    LEFT_MOTOR.set_power(FORWARD_SPEED) # Start left motor
    RIGHT_MOTOR.set_power(FORWARD_SPEED) # Simultaneously start right motor
    print("motors set up and running")

    while True:
        try:
            detect_color()
            if T_SENSOR.is_pressed(): # Press touch sensor to stop robot
                print("Button pressed")
                #. rotate(90, 180)
                BP.reset_all()
                exit()
            time.sleep(SENSOR_POLL_SLEEP) # Use sensor polling interval here
        except SensorError as error:
            print(error) # On exception or error, print error code

except KeyboardInterrupt: # Allows program to be stopped on keyboard interrupt
    BP.reset_all()
