# Pi Motion Logger

Detect movement with a PIR sensor and log each event to [meow meow scratch](https://meowmeowscratch.com). Simple activity or security monitoring.

## Wiring

| HC-SR501 PIR | Raspberry Pi |
|-------------|-------------|
| VCC         | 5V (pin 2)  |
| OUT         | GPIO17 (pin 11) |
| GND         | GND (pin 6) |

## Setup

```bash
pip install -r requirements.txt
export MEOW_API_KEY="your-key"
python motion_logger.py
```

A cooldown of 10 seconds prevents duplicate events. Edit `COOLDOWN` to adjust.

## API setup

Create an app called `pi-motion-logger` with a collection endpoint `events` and fields: `detected_at` (datetime), `label` (text).
