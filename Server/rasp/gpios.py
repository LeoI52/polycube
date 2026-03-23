import time
import sys
import os
from gpiozero import LED, Button


l1 = 18 # led for player 1 
l2 = 23 # led for player 2 
l3 = 24 # led for player 3 
l4 = 25 # led for player 4 


class GameHardware:
    def __init__(self):
        # 1. Standard LEDs (GPIO Pins 18, 23, 24, 25)
        # These can represent Health, Ammo, Level, etc.
        self.leds = [LED(l1), LED(l2), LED(l3), LED(l4)]
        
        # 2. Reset Switch (GPIO Pin 17)
        # Using internal pull-up: Button connects to Pin 17 and GND
        self.reset_btn = Button(17, hold_time=2) 
        self.reset_btn.when_pressed = self._game_reset # Tap to reset game logic
        

    # --- LED Control Methods ---
    def set_led_bar(self, count):
        """Lights up 0 to 4 LEDs based on a game value (like health)."""
        for i in range(len(self.leds)):
            if i < count:
                self.leds[i].on()
            else:
                self.leds[i].off()

    def flash_all(self, times=3):
        """Blinks all standard LEDs (e.g., for 'Level Up')."""
        for _ in range(times):
            [l.on() for l in self.leds]
            time.sleep(0.1)
            [l.off() for l in self.leds]
            time.sleep(0.1)

    # --- Grove RGB Methods ---
    def set_status_color(self, r, g, b):
        """Sets the Grove LED color (0-255)."""
        if self.rgb:
            self.rgb.set_rgb(0, r, g, b)

    # --- Reset Logic ---
    def _game_reset(self):
        print("Hardware Trigger: Resetting Game Level...")
        # You can add a flag here that your main game reads
        self.needs_reset = True