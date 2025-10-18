import brickpi3
import time
import subprocess
import signal
from utils.brick import TouchSensor, wait_ready_sensor, reset_brick


# Initialize sensor
sensor2 = TouchSensor(2)
wait_ready_sensors()

# Start both programss
drumming = subprocess.Popen(["python3", "drumming.py"])
flute = subprocess.Popen(["python3", "flute.py"])

print("Drumming and flute programs started.")

try:
    while True:
        #Detect if sensor#2 is pressed
        if sensor2.is_pressed():
            print("Sensor #2 pressed — stopping programs.")
            # Terminate both programs
            drumming.send_signal(signal.SIGINT)
            flute.send_signal(signal.SIGINT)
            drumming.terminate()
            flute.terminate()
            break
        time.sleep(0.1)  

except KeyboardInterrupt:
    drumming.terminate()
    flute.terminate()

print("All programs closed.")