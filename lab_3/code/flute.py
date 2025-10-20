from utils.brick import wait_ready_sensors, EV3ColorSensor
from utils.sound import Sound

color = EV3ColorSensor(4)  # port S4
wait_ready_sensors()

# Pre-create Sound objects (slow operation; do it once)
# duration in seconds, volume 0.0-100.0, pitch can be note name or frequency
COLOR_TO_SOUND = {
    "red": Sound(duration=0.6, volume=80, pitch="C5"),
    "green": Sound(duration=0.6, volume=80, pitch="D5"),
    "blue": Sound(duration=0.6, volume=80, pitch="E5"),
    "yellow": Sound(duration=0.6, volume=80, pitch="G5"),
}

print("Flute subsystem started.")
print("Mapped colours:", ", ".join(COLOR_TO_SOUND.keys()))
print("Show WHITE or an unmapped colour to end.")

try:
    while True:
        input("Press Enter to read colour (or Ctrl+C to quit)...")
        name = color.get_color_name()
        print("Color name:", name)

        if name is None:
            print("No color name read -> ending flute subsystem.")
            break

        key = name.lower()
        if key == "white":
            print("White detected -> ending flute subsystem.")
            break

        if key in COLOR_TO_SOUND:
            snd = COLOR_TO_SOUND[key]
            print(f"Playing {key} ({snd.pitch if hasattr(snd,'pitch') else 'note'})")
            # play and wait until done
            snd.play().wait_done()
        else:
            print(f"Color '{name}' not mapped -> ending flute subsystem.")
            break
except KeyboardInterrupt:
    print("Flute subsystem interrupted by user.")