from utils.brick import BP, EV3UltrasonicSensor, TouchSensor, Motor, wait_ready_sensors, SensorError
import time
import math
import subprocess
from utils.sound import Sound
from threading import Thread, Event
import room_detection
import globals


# DRIVING
FORWARD_SPEED = 130
SENSOR_POLL_SLEEP = 0.05

# TURNING
WHEEL_RADIUS = 0.022
AXEL_LENGTH = 0.078
ORIENTTODEG = AXEL_LENGTH / WHEEL_RADIUS
POWER_LIMIT = 80
MOTOR_POLL_DELAY = 0.05

# LINEAR MOTION
DIST_TO_DEG = 360 / (2 * math.pi * WHEEL_RADIUS)  # deg per meter
ROOM_FORWARD_DIST = 0.14  # m forward after detecting door

WALL_DST = 7.0

# SENSORS / MOTORS
us = EV3UltrasonicSensor(1)  # Ultrasonic sensor in Port 1
T_SENSOR = TouchSensor(2)    # Touch Sensor in Port S2
LEFT_MOTOR = Motor("A")      # Left motor in Port A/ actually is D
RIGHT_MOTOR = Motor("D")     # Right motor in Port D/ actually is A


def stop_robot():
    try:
        if T_SENSOR.is_pressed():  # Press touch sensor to stop robot
            print("Button pressed")
            BP.reset_all()
            exit()
        time.sleep(SENSOR_POLL_SLEEP)
    except SensorError as error:
        print(error)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def wait_for_motor(motor: Motor):
    # Wait until motor starts moving
    while math.isclose(motor.get_speed(), 0, abs_tol=1.0):
        time.sleep(MOTOR_POLL_DELAY)
    # Then wait until it stops again
    while not math.isclose(motor.get_speed(), 0, abs_tol=1.0):
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

def is_mission_complete():
    return (PACKAGES == 0) and DOOR_SCANS

def reset_all_sensors():
    
    global us, T_SENSOR

    print("[main] Resetting sensors...")

    BP.reset_all()

    us = EV3UltrasonicSensor(1)
    T_SENSOR = TouchSensor(2)

    wait_ready_sensors()

    print("[main] Sensors reinitialized successfully.")


try:
    wait_ready_sensors()

    # THREADING SETUP FOR ROOM DETECTION
    stop_detection = Event()
    room_detected = Event()
    room_detected_false = Event()

    room_thread = Thread(
        target=room_detection.room_detection_loop,
        args=(stop_detection, room_detected, room_detected_false),
        daemon=True,
    )
    room_thread.start()
    print("[main] Room detection thread started.")

    # State to track the 0.14 m window
    room_window_active = False
    room_window_start_pos = None # encoder position when Yellow/Orange first detected

    LEFT_MOTOR.set_dps(FORWARD_SPEED)
    RIGHT_MOTOR.set_dps(FORWARD_SPEED)

    Kp = 10.0
    DEADBAND = 0.3
    DEADBAND_WALL = 0.55
    DEADBAND_ROOM = 0.1


    #MAIN NAVIGATION LOOP
    LEFT_MOTOR.set_dps(FORWARD_SPEED)
    RIGHT_MOTOR.set_dps(FORWARD_SPEED)

    Kp = 10.0
    DEADBAND = 0.3
    DEADBAND_WALL = 0.55
    DEADBAND_ROOM = 0.1

    while True:
        stop_robot()

        dist = us.get_value()
        if dist is None:
            time.sleep(SENSOR_POLL_SLEEP)
            continue

        # 1) Handle room detection events from the thread

        # If we just detected a doorway and no window is active yet
        if room_detected.is_set() and not room_window_active:
            room_window_active = True
            room_window_start_pos = LEFT_MOTOR.get_position()
            room_detected_false.clear()

            # Count this door scan
            DOOR_SCANS += 1
            print(f"[main] Room window started at door #{DOOR_SCANS}: tracking 0.14 m while wall-following continues.")

        # If we are in the 0.14 m window
        if room_window_active:
            # Check how far we've travelled since the window started
            current_pos = LEFT_MOTOR.get_position()
            delta_deg = abs(current_pos - room_window_start_pos)
            dist_travelled = delta_deg / DIST_TO_DEG
            print(f"[main] Room window distance travelled: {dist_travelled:.3f} m")

            # If Red was seen in this window => cancel room entry
            if room_detected_false.is_set():
                print("[main] Room window cancelled. Red detected.")
                room_window_active = False
                room_detected.clear()
                room_detected_false.clear()
                # continue normal navigation
            # If we've gone at least 0.14 m without Red-> enter room
            elif dist_travelled >= ROOM_FORWARD_DIST:
                print("[main] Room confirmed after 0.14 m. Stopping path following and running drop_off.py")

                # Stop motors
                LEFT_MOTOR.set_dps(0)
                RIGHT_MOTOR.set_dps(0)

                # Stop detection thread
                stop_detection.set()
                room_thread.join()
                print("[main] Room detection thread stopped.")

                # Run drop_off.py
                subprocess.run(["python3", "drop_off.py"])

                snd = Sound(duration=0.6, volume=80, pitch="C5")
                snd.play().wait_done()

                # Update package count, one package delivered in this room
                global PACKAGES
                PACKAGES = max(PACKAGES - 1, 0)
                print(f"[main] Packages remaining: {PACKAGES}")

                # CHECK MISSION COMPLETION AND GO TO MAIL ROOM
                if is_mission_complete():
                    print("[main] Mission complete! Mail room reached.")
                    #  HERE WE WOULD RUN THE MISSION COMPLETION SCRIPT
                    BP.reset_all()
                    break   # end program

                reset_all_sensors()

                # Reset room window state
                room_window_active = False
                room_window_start_pos = None

                # Create new events and new thread for the next room
                stop_detection = Event()
                room_detected = Event()
                room_detected_false = Event()

                room_thread = Thread(
                    target=room_detection.room_detection_loop,
                    args=(stop_detection, room_detected, room_detected_false),
                    daemon=True,
                )
                room_thread.start()
                print("[main] Room detection thread restarted after drop_off.")

                # Resume wall-following
                LEFT_MOTOR.set_dps(FORWARD_SPEED)
                RIGHT_MOTOR.set_dps(FORWARD_SPEED)

                continue

        # 2) Wall-following navigation
        #    This continues during room detection
        error = WALL_DST - dist
        print(dist)
        print(error)

        if abs(error) <= DEADBAND:
            LEFT_MOTOR.set_dps(FORWARD_SPEED)
            RIGHT_MOTOR.set_dps(FORWARD_SPEED)
            print("go straight")
        elif error < -DEADBAND_ROOM:
            print("go right")
            left_speed = FORWARD_SPEED + (Kp * error)
            right_speed = FORWARD_SPEED - (Kp * error)
            max_speed = POWER_LIMIT
            left_speed = clamp(left_speed, -max_speed, max_speed)
            right_speed = clamp(right_speed, -max_speed, max_speed)
            LEFT_MOTOR.set_limits(POWER_LIMIT, abs(FORWARD_SPEED))
            RIGHT_MOTOR.set_limits(POWER_LIMIT, abs(FORWARD_SPEED))
            LEFT_MOTOR.set_dps(left_speed)
            RIGHT_MOTOR.set_dps(right_speed)
        elif error > DEADBAND_WALL:
            print("go left")
            left_speed = FORWARD_SPEED + (Kp * error)
            right_speed = FORWARD_SPEED - (Kp * error)
            max_speed = POWER_LIMIT
            left_speed = clamp(left_speed, -max_speed, max_speed)
            right_speed = clamp(right_speed, -max_speed, max_speed)
            LEFT_MOTOR.set_limits(POWER_LIMIT, abs(FORWARD_SPEED))
            RIGHT_MOTOR.set_limits(POWER_LIMIT, abs(FORWARD_SPEED))
            LEFT_MOTOR.set_dps(left_speed)
            RIGHT_MOTOR.set_dps(right_speed)

        time.sleep(SENSOR_POLL_SLEEP)


except KeyboardInterrupt:
    BP.reset_all()
