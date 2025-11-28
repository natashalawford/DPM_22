from utils.brick import BP, SensorError, TouchSensor
import time
import os

# Poll interval for the emergency stop touch sensor
SENSOR_POLL_SLEEP = 0.05


def stop_robot_thread():
    """Continuously poll the touch sensor and exit the process when pressed.

    This implementation recreates the TouchSensor instance if a SensorError
    occurs (for example after a `BP.reset_all()` call in the main thread).
    That prevents the stop thread from losing the ability to detect presses
    after sensors are reinitialized elsewhere in the program.
    """
    t_sensor = None
    while True:
        try:
            # Lazily create/recreate the TouchSensor object so it stays valid
            # even if main thread calls BP.reset_all() and reinitializes sensors.
            if t_sensor is None:
                t_sensor = TouchSensor(2)

            if t_sensor.is_pressed():  # Press touch sensor to stop robot
                try:
                    print("stop")
                    print("resetting brickpi")
                    BP.reset_all()
#                     while True:
#                         print("resetting brickpi")
#                         BP.reset_all()
#                         print("stopping thread")
#                         stop_robot_thread.join()
#                         time.sleep(0.1)
                except Exception:
                    # best-effort reset; continue to exit even if reset fails
                    pass
                # exit immediately
                os._exit(0)

        except SensorError:
            # Sensor object became invalid (e.g. after BP.reset_all()), clear
            # reference so we recreate it on the next loop iteration.
            t_sensor = None

        # Sleep between polls to avoid busy-looping
        time.sleep(SENSOR_POLL_SLEEP)