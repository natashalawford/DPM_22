# room_detection.py
import time
from threading import Event
from utils.brick import EV3ColorSensor, SensorError

color = EV3ColorSensor(3)

def detect_color():
    try:
        r, g, b = color.get_rgb()
        
        color_ranges = {
            "Black":  (0, 60,   0, 60,   0, 60),
            "Green":  (80, 140, 100,160, 9, 40),
            "Red":    (100,200, 7, 25,  7, 20),
            "Orange": (120,300, 40,95,  5, 20),
            "Yellow": (142,400, 101,300,13,30),
            "White":  (160,400, 140,400,110,400),
        }

        detected_color = "Unknown"

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

        return detected_color

    except SensorError:
        return "Unknown"


def room_detection_loop(stop_detection: Event,
                        room_detected: Event,
                        room_detected_false: Event):

    last_color = None

    while not stop_detection.is_set():
        current_color = detect_color()

        # Yellow/Orange = room detected
        if current_color in ("Yellow", "Orange") and last_color not in ("Yellow", "Orange"):
            print("[room_detection] Room detected.")
            room_detected.set()
            room_detected_false.clear()

        # Red  = do not enter room
        if room_detected.is_set() and current_color == "Red":
            print("[room_detection] Red detected. Do not enter.")
            room_detected_false.set()
            

        last_color = current_color
        time.sleep(0.05)

    print("[room_detection] Exiting thread.")
