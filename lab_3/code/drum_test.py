import brickpi3
import time

# DPM Hands On Example 3 (Lecture 10) - MotorDemo
# A simple interactive program that allows the user to specify rotation and
# for speed on an EV3 Large Motor. Program operates a loop until ^C entered.
# Author: F.P. Ferrie.
# Date: September 23, 2021.

# Program parameters
INIT_TIME = 1  # Initialization time (Seconds)

# Allocate resources, initial configuration
BP = brickpi3.BrickPi3()  # Create BrickPi instance
AUX_MOTOR = BP.PORT_A  # Auxiliary motor used for test.
POWER_LIMIT = 80  # Power limit %
SPEED_LIMIT = 720  # Degrees / second max
#NOTE speed 200- 300 for first design
#NOTE speed 700/720 for second design
# Entry point - print instructions.
try:
    print('BrickPi Motor Position Demo:')

    # Motor Initialization
    try:
        BP = brickpi3.BrickPi3()  # Create instance
        BP.offset_motor_encoder(AUX_MOTOR, BP.get_motor_encoder(AUX_MOTOR))  # Reset encoder
        BP.set_motor_limits(AUX_MOTOR, POWER_LIMIT, SPEED_LIMIT)  # Limit power and speed
        BP.set_motor_power(AUX_MOTOR, 0)
    except IOError as error:
        print(error)

    # Main loop - prompt for power and rotation angle; issue commands; repeat 'till ^C
    while True:
        speed = eval(input('Enter speed: '))
        rotation = eval(input('Enter rotation (+/- degrees: )'))
        try:
            # Speed associated with set_motor_position is determined by set_motor_limits.
            BP.set_motor_limits(AUX_MOTOR, POWER_LIMIT, speed)
            BP.set_motor_position_relative(AUX_MOTOR, rotation)
        except IOError as error:
            print(error)

# Program exit on ^C
except KeyboardInterrupt:
    BP.reset_all()
