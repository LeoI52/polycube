from gpiozero import LED
from signal import pause

led = LED(18)
led.blink(on_time=1, off_time=1)

pause() # Keeps the script running so the blink continues