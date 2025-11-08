import time
#!/usr/bin/env python3
"""Very small drive script.

Top of file is where the simple settings live so you can change them:
  LEFT_PORT, RIGHT_PORT, DEGREES, DPS, POWER

This version is time-based (no encoder polling). It estimates how long the
move should take using degrees/DPS and sleeps that long + 1s buffer. Simpler
to understand than a tolerance loop.
"""
import time

from utils.brick import Motor, wait_ready_sensors, reset_brick

# --- Edit these values at the top if you want different behavior ---
LEFT_PORT = "A"       # left motor port (letter)
RIGHT_PORT = "C"      # right motor port (letter)
DEGREES = 720          # how many degrees each wheel should turn
DPS = 300              # speed in degrees per second
POWER = 80             # power limit (0-100)
BUFFER_S = 1.0         # extra seconds to wait after estimated time
# ------------------------------------------------------------------


def main():
    wait_ready_sensors(True)

    left = Motor(LEFT_PORT)
    right = Motor(RIGHT_PORT)

    left.reset_encoder()
    right.reset_encoder()

    left.set_limits(power=POWER, dps=DPS)
    right.set_limits(power=POWER, dps=DPS)

    try:
        # Start both motors
        left.set_position_relative(DEGREES)
        right.set_position_relative(DEGREES)

        # Simple time estimate: degrees / dps (guard against DPS==0)
        if DPS and DPS != 0:
            wait_time = abs(DEGREES) / abs(DPS) + BUFFER_S
        else:
            wait_time = 5 + BUFFER_S

        time.sleep(wait_time)

    except KeyboardInterrupt:
        # allow user to stop early with Ctrl-C
        pass
    finally:
        # stop motors and try to reset the brick
        try:
            left.set_power(0)
            right.set_power(0)
            left.set_limits()
            right.set_limits()
        except Exception:
            pass
        try:
            reset_brick()
        except Exception:
            pass


if __name__ == "__main__":
    main()
