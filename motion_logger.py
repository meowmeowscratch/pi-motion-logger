"""
Pi Motion Logger
================
Detects movement using a PIR sensor and logs each event
to your meow meow scratch API.

Wiring (HC-SR501 PIR → Pi):
  VCC → 5V  (pin 2)
  OUT → GPIO17 (pin 11)
  GND → GND (pin 6)

Setup:
  pip install -r requirements.txt
  export MEOW_API_KEY="your-key"
  python motion_logger.py
"""

# os — access environment variables (like your API key) stored outside the code
import os
# sys — exit the program with an error code if something is wrong at startup
import sys
# time — get the current time in seconds (for cooldown math) and pause between sensor checks
import time
# datetime, timezone — create human-readable timestamps in UTC for each motion event
from datetime import datetime, timezone
# RPi.GPIO — control the Raspberry Pi's GPIO pins so we can read the PIR sensor's signal
import RPi.GPIO as GPIO
# Meow, MeowError — the meow meow scratch SDK for sending data to your cloud account
from meow_sdk import Meow, MeowError

API_KEY = os.environ.get("MEOW_API_KEY")
if not API_KEY:
    print("Set MEOW_API_KEY environment variable")
    sys.exit(1)

APP = "pi-motion-logger"
ENDPOINT = "events"
PIR_PIN = 17
# Minimum seconds between logged events. PIR sensors stay HIGH for several seconds
# after detecting motion, so without this cooldown we'd log the same event multiple
# times. 10 seconds works well for most uses — increase it if you still see duplicates.
COOLDOWN = 10

api = Meow(api_key=API_KEY)

# BCM mode: refer to pins by Broadcom chip number (GPIO17), not physical position
# (pin 11). This is the most common convention in tutorials and documentation.
GPIO.setmode(GPIO.BCM)
# Set as input. No pull-up/pull-down needed — the PIR sensor has its own output that
# drives the pin HIGH (motion) or LOW (no motion).
GPIO.setup(PIR_PIN, GPIO.IN)


def main():
    print("Motion logger running — waiting for movement")
    print("Press Ctrl+C to stop\n")

    last_event = 0

    try:
        while True:
            # Two conditions must BOTH be true:
            #   (1) PIR detects motion (pin reads HIGH)
            #   (2) Enough time has passed since the last logged event
            # time.time() returns seconds since Jan 1 1970, so subtracting two
            # timestamps gives the number of elapsed seconds between them.
            if GPIO.input(PIR_PIN) and (time.time() - last_event) > COOLDOWN:
                now = datetime.now(timezone.utc)
                data = {
                    "detected_at": now.isoformat(),
                    "label": "motion",
                }
                try:
                    api.send(APP, ENDPOINT, data)
                    print(f"[{now.strftime('%H:%M:%S')}] Motion detected!")
                except MeowError as e:
                    print(f"Send failed: {e}")

                last_event = time.time()

            # Check 5 times per second (1 / 0.2 = 5). Fast enough to catch
            # movement, slow enough not to waste CPU on the Pi.
            time.sleep(0.2)
    finally:
        # Reset all GPIO pins to their default (safe) state on exit. This runs
        # whether the program ends normally or is stopped with Ctrl+C, because
        # it's inside a "finally" block.
        GPIO.cleanup()


if __name__ == "__main__":
    main()
