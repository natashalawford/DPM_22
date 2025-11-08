from utils.brick import BP, TouchSensor, Motor, wait_ready_sensors, SensorError
import time

FORWARD_SPEED = 75        # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05  # Polling rate = 50 msec

T_SENSOR = TouchSensor(2) # Touch Sensor in Port S2
LEFT_MOTOR = Motor("A")   # Left motor in Port A
RIGHT_MOTOR = Motor("D")  # Right motor in Port D

def rotate(angle, speed):
    try:
        set_motor_limits(LEFT_MOTOR, POWER_LIMIT, speed)   # Set speed
        set_motor_limits(RIGHT_MOTOR, POWER_LIMIT, speed)
        set_motor_position_relative(LEFT_MOTOR, int(angle * ORIENTTODEG))   # Rotate L wheel +ve
        set_motor_position_relative(RIGHT_MOTOR, int(-angle * ORIENTTODEG)) # Rotate R wheel -ve
        Block(RIGHT_MOTOR)
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
                #BP.reset_all()
                rotate(90, 20)
                exit()
            time.sleep(SENSOR_POLL_SLEEP) # Use sensor polling interval here
        except SensorError as error:
            print(error) # On exception or error, print error code

except KeyboardInterrupt: # Allows program to be stopped on keyboard interrupt
    BP.reset_all()
