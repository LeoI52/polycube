from gpiozero import RGBLED, LED, Button
import threading
import time
import sys

class GPIOManager:
    def __init__(self):
        self.leds_vertes = []
        self.rgb = None
        self.bouton = None
        self._blink_thread = None
        self._stop_blink = threading.Event()

        # 1. Initialisation des LEDs Vertes
        try:
            self.leds_vertes = [LED(27), LED(17), LED(3), LED(2)]
            print("GPIO: LEDs vertes OK")
        except Exception as e:
            print(f"GPIO Error (LEDs vertes): {e}")

        # 2. Initialisation de la LED RGB
        try:
            self.rgb = RGBLED(red=16, green=20, blue=21, active_high=False)
            print("GPIO: LED RGB OK")
        except Exception as e:
            print(f"GPIO Error (RGB): {e}")

        # 3. Initialisation du Bouton (Isolée car source fréquente d'erreurs)
        try:
            # On tente l'initialisation du bouton
            self.bouton = Button(13, pull_up=False, bounce_time=0.1)
            self.bouton.when_pressed = self._on_button_pressed
            print("GPIO: Bouton OK")
        except Exception as e:
            print(f"GPIO Error (Bouton): {e}")
            print("Conseil: Si vous êtes sur Pi 5, installez 'rpi-lgpio'")

    def _on_button_pressed(self):
        print("Bouton physique pressé !")
        self.flash_all()

    def all_off(self):
        self.stop_blink()
        for led in self.leds_vertes:
            try: led.off()
            except: pass
        if self.rgb:
            try: self.rgb.off()
            except: pass

    def flash_all(self, duration=1):
        if not self.rgb and not self.leds_vertes: return
        
        try:
            if self.rgb: self.rgb.color = (1, 1, 1)
            for led in self.leds_vertes: led.on()
        except: pass
        
        def _off():
            time.sleep(duration)
            self.all_off()
        
        threading.Thread(target=_off, daemon=True).start()

    def blink_start_sequence(self):
        self.stop_blink()
        self._stop_blink.clear()
        self._blink_thread = threading.Thread(target=self._blink_loop, daemon=True)
        self._blink_thread.start()

    def _blink_loop(self):
        for _ in range(6): 
            if self._stop_blink.is_set():
                break
            try:
                for led in self.leds_vertes: led.toggle()
                if self.rgb:
                    is_on = self.leds_vertes[0].is_active if self.leds_vertes else True
                    self.rgb.color = (1, 0.5, 0) if is_on else (0, 0, 0)
            except: pass
            time.sleep(0.2)
        self.all_off()

    def stop_blink(self):
        self._stop_blink.set()
        if self._blink_thread:
            try: self._blink_thread.join(timeout=0.1)
            except: pass

    def update_controllers(self, occupied_slots):
        for i, led in enumerate(self.leds_vertes):
            slot_id = i + 1
            try:
                if occupied_slots.get(slot_id): led.on()
                else: led.off()
            except: pass

    def set_led(self, index, state):
        if 0 <= index < len(self.leds_vertes):
            try:
                if state: self.leds_vertes[index].on()
                else: self.leds_vertes[index].off()
            except: pass

    def set_rgb(self, r, g, b):
        if self.rgb:
            try: self.rgb.color = (r, g, b)
            except: pass

# Instance unique
gpio_manager = GPIOManager()
