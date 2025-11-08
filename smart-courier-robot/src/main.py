from utils.brick import BP, TouchSensor, Motor, wait_ready_sensors, SensorError
import time

#DRIVING
FORWARD_SPEED = 20        # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05  # Polling rate = 50 msec

#TURNING
WHEEL_RADIUS = 0.028
AXEL_LENGTH = 0.11
ORIENTTODEG = AXEL_LENGTH / WHEEL_RADIUS
POWER_LIMIT = 80

#PORTS
T_SENSOR = TouchSensor(2) # Touch Sensor in Port S2
LEFT_MOTOR = Motor("A")   # Left motor in Port A
RIGHT_MOTOR = Motor("D")  # Right motor in Port D

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
