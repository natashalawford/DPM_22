from utils.brick import BP, EV3UltrasonicSensor, TouchSensor, Motor, wait_ready_sensors, SensorError, EV3ColorSensor
from utils import sound
import time
import math
import sys
from threading import Thread
from stop_robot import stop_robot_thread
DOOR_SCANS = 2
#DOOR_SCANS = int(sys.argv[1])

#DRIVING
FORWARD_SPEED = 100        # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05  # Polling rate = 50 msec

#TURNING
WHEEL_RADIUS = 0.022
AXEL_LENGTH = 0.078
ORIENTTODEG = AXEL_LENGTH / WHEEL_RADIUS
DIST_TO_DEG = 180/(math.pi*WHEEL_RADIUS)
POWER_LIMIT = 110
MOTOR_POLL_DELAY = 0.05
TURNING = "neutral"

#PORTS
T_SENSOR = TouchSensor(2) # Touch Sensor in Port S2
LEFT_MOTOR = Motor("D")   # Left motor in Port D
RIGHT_MOTOR = Motor("A")  # Right motor in Port A

#Path following distance from wall
WALL_DST = 5.7
us = EV3UltrasonicSensor(1) # Ultrasonic sensor in Port 1
Kp = 20.0         
DEADBAND = 0.3

#SOUND
SOUND = sound.Sound(duration=0.3, pitch="A4", volume=60)

def init_motor(motor: Motor):
    """Function to initialize a motor"""
    try:
        motor.set_dps(0)
        ensure_motor_stopped(motor)
        motor.reset_encoder() # Reset encoder to 0 value
        motor.set_limits(POWER_LIMIT, FORWARD_SPEED) # Set power and speed limits
        
    except IOError as error:
        print(error)

def rotate(angle, speed):
    try:
        print("rotating")
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)   # Set speed
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)   # Set speed
        LEFT_MOTOR.set_position_relative(int(angle * ORIENTTODEG))   # Rotate L wheel +ve
        RIGHT_MOTOR.set_position_relative(int(-angle * ORIENTTODEG)) # Rotate R wheel -ve
        wait_for_motor(RIGHT_MOTOR)
        wait_for_motor(LEFT_MOTOR)
    except IOError as error:
        print(error)

def wait_for_motor(motor: Motor):
    print("Waiting for motor to start")
    start = time.time()
    while abs(motor.get_speed()) < 1:
        if time.time() - start > 1:
            print("Motor did not start (timeout)")
            break
        time.sleep(0.01)

    print("Motor moving... waiting to finish")
    while abs(motor.get_speed()) >= 1:
        print("speed =", motor.get_speed())
        time.sleep(0.01)

    print("Motor finished")

def ensure_motor_stopped(motor: Motor):
    motor.set_dps(0)  # Command stop
    time.sleep(0.05)  # Give the command time
    while not math.isclose(motor.get_speed(), 0, abs_tol=1):
        time.sleep(0.05)

def move_dist_fwd(distance, speed): # meters, dps
    """Function to move forward by user-specified distance and speed"""
    try:
        print("fwd")
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)

        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        print("speed set")
        LEFT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG)) # Rotate wheels
        RIGHT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))

        wait_for_motor(RIGHT_MOTOR)
        wait_for_motor(LEFT_MOTOR)
    except IOError as error:
        print(error)
        
def play_sound():
    SOUND.play()
    SOUND.wait_done()

def main():
    wait_ready_sensors()
    init_motor(LEFT_MOTOR) # Initialize L Motor
    init_motor(RIGHT_MOTOR) # Initialize R Motor
    print("motor initialized")

    stop_thread = Thread(target=stop_robot_thread, daemon=True)
    stop_thread.start()
    
    try:
        print("DOOR_SCANS: ", DOOR_SCANS)

        #Paths 1, 3
        if DOOR_SCANS == 2 or DOOR_SCANS == 4: #need to fix: when this if statement gets issued with doorcount, startsrunning main, or just 
             print("Taking path 1")
         
             #go backwards 24.5 cm using path correction
             move_dist_fwd(-0.25, FORWARD_SPEED)
             
             #rotate 90 degrees counterclockwise
             #todo: implement rotation using gyro
             rotate(-90, 180)
             
             #go forwards 50 cm into mail room
             move_dist_fwd(0.57, FORWARD_SPEED)
             
             #play sound
             play_sound()


        #might need to update this depending on how door scans is updated by malak  
        #Path 2
        elif DOOR_SCANS == 5: 
            print("Taking path 2")
            
            #go forward 24.5 cm using path correction
            move_dist_fwd(0.245, FORWARD_SPEED)
            
            #rotate 90 degrees counterclockwise
            #todo: implement using gyroscope
            rotate(-90, 180)
            
            #go forwards 48.5cm using path correction
            move_dist_fwd(0.51, FORWARD_SPEED)
            
            #rotate 90 degrees counterclockwise
            #todo: implement using gyroscope
            rotate(-90, 180)
            
            #go forwards 50 cm into mail room
            move_dist_fwd(0.57, FORWARD_SPEED)
            
            #play sound
            play_sound()
        
        #while True:
            #stop_robot()
            #rotate 90 degrees counterclockwise using gyroscope
            

    except KeyboardInterrupt: # Abort program using ^C (Ctrl+C)
        BP.reset_all()

if __name__ == "__main__":
    main()