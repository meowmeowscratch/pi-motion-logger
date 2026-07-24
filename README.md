# Pi Motion Logger

Catch every movement! This project uses a PIR (Passive Infrared) motion sensor to detect when someone or something moves nearby, and logs each event to the internet with a timestamp. Use it as a security monitor, a pet tracker, or just to see how often people walk through a room.

---

## What you'll learn

By building this project, you will learn:

- **How PIR motion sensors work** -- they detect changes in infrared (heat) radiation to sense when a warm body moves through their field of view.
- **GPIO digital input** -- reading a simple HIGH/LOW signal from a sensor pin on the Raspberry Pi.
- **Cooldown timers** -- preventing duplicate events when a sensor stays triggered for several seconds.
- **Timestamps and logging** -- recording the exact time of each event and sending it to a cloud API so you can review activity later.

---

## What you'll need

### Hardware

| Component | Description |
|-----------|-------------|
| **Raspberry Pi** | Any model with GPIO pins (Pi 3, Pi 4, Pi Zero, etc.). You will also need a power supply, an SD card with Raspberry Pi OS installed, and a way to access the terminal (monitor + keyboard, or SSH). |
| **HC-SR501 PIR motion sensor** | A dome-shaped sensor that detects changes in infrared (heat) radiation. When a warm body (person, pet) moves in front of it, it outputs a HIGH signal. Range is about 3-7 meters with a 120-degree detection angle. It has two small orange knobs on the back: one for sensitivity, one for how long the signal stays HIGH. |
| **Three jumper wires** | Female-to-female jumper wires. You need three: one for power (red), one for the signal (yellow), and one for ground (black). The colors do not matter electrically, but using different colors makes it much easier to check your wiring. |

### Software

| Software | What it is |
|----------|------------|
| **Python 3** | The programming language we write our code in. It comes pre-installed on Raspberry Pi OS. Open a terminal and type `python3 --version` to confirm. |
| **meow meow scratch account** | A free cloud service where your motion events will be stored. Sign up at [meowmeowscratch.com](https://meowmeowscratch.com) and get your API key from the dashboard. |

---

## Wiring diagram

Connect the three pins on the HC-SR501 to your Raspberry Pi using jumper wires. The sensor has three pins in a row, usually labeled **VCC**, **OUT**, and **GND**.

```
    Raspberry Pi               HC-SR501 PIR
    +-----------+              +----------+
    |           |              |  (dome)  |
    | 5V     o--+----- red ----+-- VCC    |
    | (pin 2)   |              |          |
    |           |              |          |
    | GPIO17 o--+--- yellow ---+-- OUT    |
    | (pin 11)  |              |          |
    |           |              |          |
    | GND    o--+---- black ---+-- GND    |
    | (pin 6)   |              +----------+
    +-----------+

    Mount the sensor with the dome facing the area you want to monitor.
    Give it 30-60 seconds to warm up after first powering on.
```

### Pin reference table

| HC-SR501 pin | Wire color | Raspberry Pi pin | What it does |
|-------------|------------|-----------------|--------------|
| VCC | Red | 5V (physical pin 2) | Provides power to the sensor. The HC-SR501 needs 5V to operate. |
| OUT | Yellow | GPIO17 (physical pin 11) | The signal line. Goes HIGH (3.3V) when motion is detected, LOW (0V) otherwise. |
| GND | Black | GND (physical pin 6) | Ground -- completes the electrical circuit. |

> **Tip:** "Physical pin" numbers count the pins on the board from top-left (pin 1) in order. "GPIO" numbers refer to the Broadcom chip's own numbering. They are different! Our code uses the GPIO (Broadcom) numbers.

---

## Step-by-step setup

### 1. Wire up the sensor

Follow the wiring diagram above. Double-check each connection before powering on the Pi. A wrong connection will not damage anything, but the sensor will not work.

### 2. Open a terminal on your Raspberry Pi

You can use a monitor and keyboard plugged directly into the Pi, or connect over SSH from another computer. All the commands below are typed into the terminal.

### 3. Install required Python packages

Python packages are add-on libraries that other people have written so you do not have to start from scratch. We install them with a tool called **pip** (Python's package manager).

First, navigate to the project folder:

```bash
cd pi-motion-logger
```

Then install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs two packages:

- **RPi.GPIO** -- lets Python talk to the GPIO pins on the Raspberry Pi so we can read the sensor.
- **meow-sdk** -- the official Python library for sending data to your meow meow scratch account.

> **What is `requirements.txt`?** It is a simple text file that lists the packages your project needs, one per line. Running `pip install -r requirements.txt` installs them all at once.

### 4. Set your API key

An **environment variable** is a value stored in your terminal session that programs can read. We use one to keep your secret API key out of the code itself (so you never accidentally share it).

```bash
export MEOW_API_KEY="your-key-here"
```

Replace `your-key-here` with the actual API key from your meow meow scratch dashboard. This key proves to the server that you are allowed to send data.

> **Note:** This `export` command only lasts for your current terminal session. If you close the terminal and open a new one, you will need to run it again. For a permanent solution, you can add the line to your `~/.bashrc` file.

> **Which kind of key should you use?** Your account offers two. A **platform token** works across every app you own. An **app API key** works for one app only. For a Pi that sits running for days, use an **app API key** — if it ever leaks, only this one app is affected, not your whole account. You'll find both in your account settings.

### 5. Set up your API collection (see the API setup section below)

Before running the code, you need to create a place in your meow meow scratch account where the motion events will be stored. See the **API setup** section below for step-by-step instructions.

### 6. Run the logger

```bash
python motion_logger.py
```

You should see:

```
Motion logger running — waiting for movement
Press Ctrl+C to stop
```

Wait 30-60 seconds for the sensor to warm up (it may trigger a few false positives during this time). Then walk in front of the sensor -- you should see a message like:

```
[14:23:07] Motion detected!
```

Each detection is automatically sent to your meow meow scratch account. Press **Ctrl+C** at any time to stop the program.

---

## How the code works

### The polling loop

The program runs an infinite loop that checks the sensor 5 times per second (every 0.2 seconds). Each time through the loop, it asks: "Is the PIR pin HIGH right now?" If yes, motion has been detected.

```
while True:
    check sensor -> if motion detected, log it
    wait 0.2 seconds
    repeat
```

This is called **polling** -- repeatedly checking a sensor for changes. It is the simplest approach and works great for this project.

### The cooldown mechanism

Without a cooldown, a single wave of your hand might trigger 10 events because the sensor stays HIGH for a while. Here is why:

1. You walk past the sensor.
2. The PIR detects your body heat and sets its output pin HIGH.
3. The pin stays HIGH for 2-5 seconds (controlled by the knob on the back of the sensor).
4. During those seconds, the loop checks the sensor 5 times per second -- that is 10-25 checks, all seeing HIGH.

The cooldown solves this by recording the time of each logged event and ignoring any new HIGH readings until enough seconds have passed. The default is 10 seconds. You can change the `COOLDOWN` variable in the code to any number that works for your situation.

### The collection endpoint pattern

When motion is detected, the code sends a small packet of data to your meow meow scratch account:

```python
{
    "detected_at": "2026-02-26T14:23:07+00:00",   # When the motion happened (UTC)
    "label": "motion"                                # A label for the event type
}
```

This is sent to the **collection endpoint** you created (see API setup below). You can view, filter, and graph these events on your meow meow scratch dashboard.

---

## API setup

Before running the logger, you need to set up a place to store the events on meow meow scratch.

1. Log in to your account at [meowmeowscratch.com](https://meowmeowscratch.com).
2. Create a new app called **`pi-motion-logger`**.
3. Inside that app, create a **collection endpoint** called **`events`**.
4. Add two fields to the `events` collection:

| Field name | Type | Description |
|-----------|------|-------------|
| `detected_at` | datetime | The timestamp of when motion was detected. |
| `label` | text | A label describing the event (the code sends `"motion"`). |

5. Copy your **API key** from the dashboard -- you will need it for the `MEOW_API_KEY` environment variable.

Once this is set up, every motion event the Pi detects will appear in your `events` collection, where you can view it from any device.

---

## Troubleshooting

### The sensor triggers constantly (false positives)

- **Adjust the sensitivity knob.** The HC-SR501 has two small orange knobs on its back. One controls sensitivity -- turn it counter-clockwise to reduce sensitivity. Start low and increase until it reliably detects real movement.
- **Avoid pointing at heat sources.** Heaters, sunny windows, and air vents can cause false triggers because the sensor detects changes in heat, not just body heat.
- **Wait for warm-up.** The sensor needs 30-60 seconds after power-on to stabilize. False triggers during this period are normal.

### No detections at all

- **Check your wiring.** Make sure VCC goes to 5V (not 3.3V), OUT goes to GPIO17, and GND goes to GND. A loose jumper wire is the most common problem.
- **Wait for warm-up.** If you just powered on, give it a full 60 seconds.
- **Check the detection range.** Walk within 1-2 meters of the sensor dome. If the sensitivity knob is turned all the way down, you may need to be very close.
- **Test the pin directly.** In a Python shell, try:
  ```python
  import RPi.GPIO as GPIO
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(17, GPIO.IN)
  print(GPIO.input(17))   # Should print 1 when motion is detected
  GPIO.cleanup()
  ```

### Duplicate events being logged

- **Increase the cooldown.** Open `motion_logger.py` and change `COOLDOWN = 10` to a larger number (e.g., `COOLDOWN = 30` for 30 seconds between events).
- **Adjust the sensor's time-delay knob.** The second orange knob on the HC-SR501 controls how long the output stays HIGH after detecting motion. Turning it counter-clockwise reduces this time.

### GPIO warnings in the terminal

If you see a message like `RuntimeWarning: This channel is already in use`, it usually means the previous run did not clean up properly (maybe the program crashed). This warning is harmless -- the code will still work. To avoid it, always stop the program with **Ctrl+C** (which triggers the cleanup code) instead of closing the terminal window.

### "Set MEOW_API_KEY environment variable" error

You need to set the API key before running the script. Run:

```bash
export MEOW_API_KEY="your-key-here"
```

Make sure you replace `your-key-here` with your actual key, and make sure you are running the script in the same terminal session where you set the variable.

### "Send failed" errors

- Check that your meow meow scratch app is named exactly `pi-motion-logger` and the collection endpoint is named exactly `events`.
- Verify that your API key is correct and has not expired.
- Make sure your Raspberry Pi has an internet connection (`ping google.com` to test).
