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

import os
import sys
import time
from datetime import datetime, timezone
import RPi.GPIO as GPIO
from meow_sdk import Meow, MeowError

API_KEY = os.environ.get("MEOW_API_KEY")
if not API_KEY:
    print("Set MEOW_API_KEY environment variable")
    sys.exit(1)

APP = "pi-motion-logger"
ENDPOINT = "events"
PIR_PIN = 17
COOLDOWN = 10  # seconds between logged events

api = Meow(api_key=API_KEY)

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)


def main():
    print("Motion logger running — waiting for movement")
    print("Press Ctrl+C to stop\n")

    last_event = 0

    try:
        while True:
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

            time.sleep(0.2)
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
