from utils.brick import BP, EV3UltrasonicSensor, TouchSensor, Motor, wait_ready_sensors, SensorError, EV3ColorSensor, EV3GyroSensor
import time
import math
import subprocess
from utils.sound import Sound
from threading import Thread, Event
import room_detection
import globals


#DRIVING
FORWARD_SPEED = 100        # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05

#TURNING
WHEEL_RADIUS = 0.022
AXEL_LENGTH = 0.078
ORIENTTODEG = AXEL_LENGTH / WHEEL_RADIUS
POWER_LIMIT = 110
MOTOR_POLL_DELAY = 0.05
TURNING = "neutral"

# LINEAR MOTION
DIST_TO_DEG = 360 / (2 * math.pi * WHEEL_RADIUS)  # deg per meter
ROOM_FORWARD_DIST = 0.14  # m forward after detecting door

WALL_DST = 7.0



#PORTS
T_SENSOR = TouchSensor(2) # Touch Sensor in Port S2
LEFT_MOTOR = Motor("D")   # Left motor in Port A
RIGHT_MOTOR = Motor("A")  # Right motor in Port D
color = EV3ColorSensor(3) # Color in port 3
gyro = EV3GyroSensor(4)   # Gyro in port 4
us = EV3UltrasonicSensor(1) # Ultrasonic sensor in Port 1

#PATH CORRECTION
Kp = 10.0
DEADBAND = 0.1


def stop_robot():
    try:
        if T_SENSOR.is_pressed():  # Press touch sensor to stop robot
            print("Button pressed")
            BP.reset_all()
            exit()
        time.sleep(SENSOR_POLL_SLEEP)
    except SensorError as error:
        print(error)
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

def clamp(v, lo, hi):
    return max(lo, min(hi, v))


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

def is_mission_complete():
    return (globals.PACKAGES == 0) and globals.DOOR_SCANS

def reset_all_sensors():
    
    global us, T_SENSOR, color, gyro

    print("[main] Resetting sensors...")

    BP.reset_all()

    us = EV3UltrasonicSensor(1)
    T_SENSOR = TouchSensor(2)
    color = EV3ColorSensor(3)
    gyro = EV3GyroSensor(4) 

    wait_ready_sensors()

    print("[main] Sensors reinitialized successfully.")

def is_color_sustained(target, samples=3, delay=SENSOR_POLL_SLEEP):
    """Return True if `target` is read in the majority of `samples`."""
    matches = 0
    for _ in range(samples):
        c = color.get_color_name()
        if c == target.lower():
            matches += 1
        time.sleep(delay)
    return matches >= (samples // 2) + 1



def main():
    try:
        wait_ready_sensors()
        angle = gyro.get_abs_measure()
        #print(f"gyro angle: {angle}")

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
        stop_room_detection = False
        stop_room_detection_start_pos = None
        just_rotated = False


        while True:
            stop_robot()

            print(f"Door count: {globals.DOOR_SCANS}")
            # Gyroscope
            new_angle = gyro.get_abs_measure()
            #print(f"gyro angle: {new_angle}")
            
            # Path correction
            dist = us.get_value()
            error = WALL_DST - dist
            path_correction(dist, error)

            # 1) Handle room detection events from the thread

            # If we just detected a doorway and no window is active yet
            if room_detected.is_set() and not room_window_active and not stop_room_detection and not just_rotated:
                room_window_active = True
                room_window_start_pos = LEFT_MOTOR.get_position()
                room_detected_false.clear()

                # Count this door scan
                globals.DOOR_SCANS += 1
                print(f"[main] Room window started at door #{globals.DOOR_SCANS}: tracking 0.14 m while wall-following continues.")

            # If we are in the 0.14 m window
            if room_window_active and not just_rotated:
                # Check how far we've travelled since the window started
                current_pos = LEFT_MOTOR.get_position()
                delta_deg = abs(current_pos - room_window_start_pos)
                dist_travelled = delta_deg / DIST_TO_DEG
                print(f"[main] Room window distance travelled: {dist_travelled:.3f} m")

                # If Red was seen in this window => cancel room entry
                if room_detected_false.is_set():
                    print("[main] Room window cancelled. Red detected.")
                    room_window_active = False
                    stop_room_detection = True
                    stop_room_detection_start_pos = LEFT_MOTOR.get_position()
                    room_detected.clear()
                    room_detected_false.clear()
                    # continue normal navigation
                # If we've gone at least 0.14 m without Red-> enter room
                elif dist_travelled >= ROOM_FORWARD_DIST and not room_detected_false.is_set():
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
                    #global globals.PACKAGES
                    globals.PACKAGES = max(globals.PACKAGES - 1, 0)
                    print(f"[main] globals.PACKAGES remaining: {globals.PACKAGES}")

                    # CHECK MISSION COMPLETION AND GO TO MAIL ROOM
                    if is_mission_complete():
                        print("[main] Mission complete! Go to mail room.")
                        # Run mission_completion.py
                        subprocess.run(["python3", "mission_completion.py"])
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
                    
                    stop_room_detection = True
                    stop_room_detection_start_pos = LEFT_MOTOR.get_position()
                    print("[main] stop_room_detection active after drop_off, ignoring doors for 0.14 m.")

                    # Resume wall-following
                    LEFT_MOTOR.set_dps(FORWARD_SPEED)
                    RIGHT_MOTOR.set_dps(FORWARD_SPEED)

                    continue

            if stop_room_detection:
                current_pos = LEFT_MOTOR.get_position()
                delta_deg = abs(current_pos - stop_room_detection_start_pos)
                dist_travelled = delta_deg / DIST_TO_DEG
                print(f"[main] Stop room detection distance: {dist_travelled:.3f} m")

                if dist_travelled >= ROOM_FORWARD_DIST:
                    print("[main] 0.14 m reached, room detection re-enabled.")
                    stop_room_detection = False
                    stop_room_detection_start_pos = None
                    room_detected.clear()
                    room_detected_false.clear()

            if just_rotated:
                current_pos = LEFT_MOTOR.get_position()
                delta_deg = abs(current_pos - stop_room_detection_start_pos)
                dist_travelled = delta_deg / DIST_TO_DEG
                print(f"[main] Stop room detection distance: {dist_travelled:.3f} m")

                if dist_travelled >= 0.40:
                    print("[main] 0.30 m reached, after turn corner, room detection re-enabled.")
                    just_rotated = False
                    stop_room_detection_start_pos = None
                    #room_detected.clear()
                    #room_detected_false.clear()

            # 2) Handle turning corners
            
            detected_color = detect_color()
            turn_start_postion = LEFT_MOTOR.get_position()
            if detected_color == "white" and (globals.DOOR_SCANS == 2 or globals.DOOR_SCANS == 3) and not just_rotated:
            # require sustained white reading to avoid false positives
                current_pos = LEFT_MOTOR.get_position()
                delta_deg = abs(current_pos - turn_start_postion)
                dist_travelled = delta_deg / DIST_TO_DEG
                print(f"[main] Start white distance before turn: {dist_travelled:.3f} m")
                while dist_travelled < 0.12:
                   LEFT_MOTOR.set_dps(FORWARD_SPEED)
                   RIGHT_MOTOR.set_dps(FORWARD_SPEED)     
                if dist_travelled >= 0.12:
                    print("[main] 0.12 m reached, initiating turn at corner.")
                    rotate(90, 180)
                    # small pause to let motors settle and to move off the patch
                    time.sleep(0.2)
                    just_rotated = True
                    continue

            time.sleep(SENSOR_POLL_SLEEP)


    except KeyboardInterrupt:
        BP.reset_all()

if __name__ == "__main__":
    main()