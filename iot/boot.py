# boot.py — runs automatically before main.py on every power-on.
# Keep this file minimal. main.py does all the real work.
import machine
import time
# Built-in blue LED (pin 2 on most ESP32 dev boards)
# Blinks 3x on boot so you know the device powered on correctly.
try:
    led = machine.Pin(2, machine.Pin.OUT)
    for _ in range(3):
        led.value(1)
        time.sleep_ms(150)
        led.value(0)
        time.sleep_ms(150)
    led.value(1)   # stays on while main.py runs
except Exception:
    pass           # skip if the board has no pin 2 LED
