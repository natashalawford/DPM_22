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

def drive_fwd_detect_room_and_center(max_time, speed):
    """
    Phase 1: Drive forward and detect entering the room.
    - Drive forward at given speed (dps).
    - Poll color sensor.
    - When color becomes Yellow/Orange, mark 'room entered' and stop.
    - Also stop if max_time is reached or touch sensor is pressed.
    """

    global LAST_COLOR

    room_entered = False
    LAST_COLOR = None 

    # Driving forward
    LEFT_MOTOR.set_limits(POWER_LIMIT, abs(speed))
    RIGHT_MOTOR.set_limits(POWER_LIMIT, abs(speed))
    LEFT_MOTOR.set_dps(speed)
    RIGHT_MOTOR.set_dps(speed)

    start_time = time.time()

    try:
        while True:
            if T_SENSOR.is_pressed():
                print("Touch sensor pressed – stopping.")
                break
            
            #stopping after certain time interval/not using US sensor for distance
            elapsed = time.time() - start_time
            if elapsed >= max_time:
                print("Reached max drive time, stopping.")
                break

            #Detect color for room detection 
            current_color = detect_color()

            if not room_entered and current_color in ("Yellow", "Orange"):
                if LAST_COLOR not in ("Yellow", "Orange"):
                    room_entered = True
                    print(f"Entered room")
                    break
                if LAST_COLOR in ("Red"):
                    room_entered = False
                    print(f"Entered room from Red")
                    break

            LAST_COLOR = current_color

            time.sleep(SENSOR_POLL_SLEEP)

    finally:
        LEFT_MOTOR.set_dps(0)
        RIGHT_MOTOR.set_dps(0)
        print("end")
