from utils.brick import BP, EV3UltrasonicSensor, TouchSensor, Motor, wait_ready_sensors, SensorError, EV3ColorSensor, EV3GyroSensor
import time
import math
import subprocess
from utils.sound import Sound
from threading import Thread, Event
import room_detection
from stop_robot import stop_robot_thread
import globals

LEFT_MOTOR = Motor("D")   # Left motor in Port A
RIGHT_MOTOR = Motor("A")  # Right motor in Port D
color = EV3ColorSensor(3) # Color in port 3
gyro = EV3GyroSensor(4)   # Gyro in port 4
us = EV3UltrasonicSensor(1) # Ultrasonic sensor in Port 1
T_SENSOR = TouchSensor(2) # Touch Sensor in Port S2

SENSOR_POLL_SLEEP = 0.05

#TURNING
WHEEL_RADIUS = 0.022
AXEL_LENGTH = 0.078
ORIENTTODEG = AXEL_LENGTH / WHEEL_RADIUS
POWER_LIMIT = 125
MOTOR_POLL_DELAY = 0.05
TURNING = "neutral"

# LINEAR MOTION
DIST_TO_DEG = 360 / (2 * math.pi * WHEEL_RADIUS)  # deg per meter

def wait_for_motor(motor: Motor):
    while math.isclose(motor.get_speed(), 0):
        time.sleep(MOTOR_POLL_DELAY)
    while not math.isclose(motor.get_speed(), 0):
        time.sleep(MOTOR_POLL_DELAY)

def rotate(angle, speed):
    try:
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)
        LEFT_MOTOR.set_position_relative(int(angle * ORIENTTODEG))    # L wheel +ve
        RIGHT_MOTOR.set_position_relative(int(-angle * ORIENTTODEG))  # R wheel -ve
        wait_for_motor(RIGHT_MOTOR)
        print("i wanna rotate")
    except IOError as error:
        print(error)
        
def gyro_correction(current_angle, target_angle):
    curr = current_angle
    # if angle is less than target rotate right
    if curr < target_angle:
        while(curr < target_angle):
            LEFT_MOTOR.set_power(10)
            RIGHT_MOTOR.set_power(-10)
            time.sleep(0.1)
            LEFT_MOTOR.set_power(0)
            RIGHT_MOTOR.set_power(0)
            wait_for_motor(RIGHT_MOTOR)
            curr = gyro.get_abs_measure
            print(f"[gyro adjustment] Angle after slight rotation: {curr}")
    
    # if angle is greater than target, rotate left
    else:
        while(curr > target_angle):
            LEFT_MOTOR.set_power(10)
            RIGHT_MOTOR.set_power(-10)
            time.sleep(0.1)
            LEFT_MOTOR.set_power(0)
            RIGHT_MOTOR.set_power(0)
            wait_for_motor(RIGHT_MOTOR)
            curr = gyro.get_abs_measure
            print(f"[gyro adjustment] Angle after slight rotation: {curr}")
        
def main():
    try:
        print("wrs")
        wait_ready_sensors(True)
        print("done")
        angle = gyro.get_abs_measure()
        print(f"gyro angle: {angle}")
        
        while True:
            new_angle = gyro.get_abs_measure()
            print(f"new gyro angle: {new_angle}")
            
            if(T_SENSOR.is_pressed):
                new_angle = gyro.get_abs_measure()
                print(f"angle beofre gyro adjustment: {new_angle}")
                time.sleep(5)
                if new_angle != 0:
                    gyro_correction(new_angle, 0)
                    correction_angle = gyro.get_abs_measure()
                    print(f"angle after correction: {correction_angle}")
                    time.sleep(5)
                
            
            time.sleep(SENSOR_POLL_SLEEP)
    except KeyboardInterrupt:
        BP.reset_all()

if __name__ == "__main__":
    main()