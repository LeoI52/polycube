from gpiozero import LED
from signal import pause
from time import sleep

# Initialize the LEDs on GPIO pins 17 and 27
led_one = LED(17)
led_two = LED(27)

print("Blinking LEDs... Press Ctrl+C to stop.")

try:
    while True:
        # Turn both on
        led_one.on()
        led_two.on()
        sleep(1) 
        
        # Turn both off
        led_one.off()
        led_two.off()
        sleep(1)

except KeyboardInterrupt:
    # Clean up is handled automatically by gpiozero
    print("\nProgram stopped.")