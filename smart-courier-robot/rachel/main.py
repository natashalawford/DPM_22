from utils.brick import BP, EV3UltrasonicSensor, TouchSensor, Motor, wait_ready_sensors, SensorError, EV3ColorSensor, EV3GyroSensor
import time
import math
import globals

#DRIVING
FORWARD_SPEED = 100        # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05  # Polling rate = 50 msec

#TURNING
WHEEL_RADIUS = 0.022
AXEL_LENGTH = 0.078
ORIENTTODEG = AXEL_LENGTH / WHEEL_RADIUS
POWER_LIMIT = 110
MOTOR_POLL_DELAY = 0.05
TURNING = "neutral"

# State for detecting Yellow -> Green transitions
LAST_COLOR = None
WALL_DST = 7.4

us = EV3UltrasonicSensor(1) # Ultrasonic sensor in Port 1

#PORTS
T_SENSOR = TouchSensor(2) # Touch Sensor in Port S2
LEFT_MOTOR = Motor("D")   # Left motor in Port A
RIGHT_MOTOR = Motor("A")  # Right motor in Port D
color = EV3ColorSensor(3) # Color in port 3
gyro = EV3GyroSensor(4)   # Gyro in port 4

#PATH CORRECTION
Kp = 10.0
DEADBAND = 0.1

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
    

def detect_color():
    """Detect color based on RGB value ranges"""
    try:
        r, g, b = color.get_rgb()
        print(f"RGB: {r}, {g}, {b}")
        
        # Define color ranges (R_min, R_max, G_min, G_max, B_min, B_max)
        color_ranges = {
            "Black": (0, 60, 0, 60, 0, 60),
            "Green": (80, 140, 100, 160, 9, 40),
            "Red": (100, 200, 7, 25, 7, 20),
            "Orange": (120, 300, 40, 95, 5, 20),
            "Yellow": (142, 400, 101, 300, 13, 30),
            "White": (160, 400, 140, 400, 110, 400)
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
            
        elif (color_ranges["White"][0] <= r <= color_ranges["White"][1] and
              color_ranges["White"][2] <= g <= color_ranges["White"][3] and
              color_ranges["White"][4] <= b <= color_ranges["White"][5]):
            detected_color = "White"
        
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

def path_correction(dist, error):
    # small errors -> keep straight to avoid hunting
        if abs(error) <= DEADBAND:
            LEFT_MOTOR.set_dps(FORWARD_SPEED)
            print(f"left speed: {FORWARD_SPEED}")
            RIGHT_MOTOR.set_dps(FORWARD_SPEED)
            print(f"right speed: {FORWARD_SPEED}")
            print("go straight")
            return
            
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
            return
            
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
            return
        

def main():
    try:
        wait_ready_sensors() # Wait for sensors to initialize
        LEFT_MOTOR.set_dps(FORWARD_SPEED)
        RIGHT_MOTOR.set_dps(FORWARD_SPEED)
        angle = gyro.get_abs_measure()
        while True:
            stop_robot()
            
            #Testing gyro
            # new_angle = gyro.get_abs_measure()
            # print(f"gyro angle: {new_angle}")
            
            dist = us.get_value()
            error = WALL_DST - dist
            #print(dist)
            path_correction(dist, error)

            #detect_color()
            
            time.sleep(SENSOR_POLL_SLEEP)
            

    except KeyboardInterrupt: # Allows program to be stopped on keyboard interrupt
        BP.reset_all()


if __name__ == "__main__":
    main()






