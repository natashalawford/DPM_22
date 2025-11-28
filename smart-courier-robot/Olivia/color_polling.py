from utils.brick import wait_ready_sensors, EV3ColorSensor, BP, TouchSensor, Motor, SensorError
import time
import globals
from threading import Thread
from stop_robot import stop_robot_thread

color = EV3ColorSensor(3)
T_SENSOR = TouchSensor(2)

SWEEP_ARM = Motor("C")
wait_ready_sensors()

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

try:
    wait_ready_sensors()
    
    while globals.SWEEPS < 10:
        detected_color = detect_color()
        print("Color name:", detected_color)
        key = detected_color.lower()

        # Used red for testing dropped off - we need to use better color detection
        # If I could get help with this, that'd be great
        if key == "green":
            globals.COLOR = "Green"
            SWEEP_ARM.set_power(0)
            break

        time.sleep(0.01)

except KeyboardInterrupt:
    BP.reset_all()