from gpiozero import RGBLED, LED, Button
import threading
import time

class GPIOManager:
    def __init__(self):
        self.leds_vertes = []
        self.rgb = None
        self.bouton = None
        self._stop_blink = threading.Event()

        try:
            self.leds_vertes = [LED(27), LED(17), LED(3), LED(2)]
            self.rgb = RGBLED(red=16, green=20, blue=21, active_high=False)
            self.bouton = Button(13, pull_up=False, bounce_time=0.1)
            self.bouton.when_pressed = self._on_button_pressed
            print("GPIO: Matériel initialisé.")
        except Exception as e:
            print(f"GPIO: Erreur matériel (normal sur PC): {e}")

    def _on_button_pressed(self):
        self.flash_all(0.5)

    def startup_sequence(self):
        """Clignotement de 5 secondes pour confirmer le démarrage."""
        print("GPIO: Lancement de la séquence de démarrage (5s)...")
        for i in range(10): # 10 x 0.5s = 5s
            try:
                for led in self.leds_vertes: led.toggle()
                if self.rgb:
                    colors = [(1,0,0), (0,1,0), (0,0,1), (1,1,0), (1,0,1)]
                    self.rgb.color = colors[i % len(colors)]
            except: pass
            time.sleep(0.5)
        self.all_off()
        print("GPIO: Séquence terminée.")

    def tag(self):
        try:
            self.set_rgb(1, 0, 0)
        except: pass
        self.all_off()

    def all_off(self):
        for led in self.leds_vertes:
            try: led.off()
            except: pass
        if self.rgb:
            try: self.rgb.off()
            except: pass

    def blink_start_sequence(self):
        threading.Thread(target=self._blink_loop, daemon=True).start()

    def _blink_loop(self):
        for _ in range(6):
            try:
                for led in self.leds_vertes: led.toggle()
                if self.rgb: self.rgb.color = (1, 0.5, 0) if self.leds_vertes[0].is_active else (0, 0, 0)
            except: pass
            time.sleep(0.2)
        self.all_off()

    def update_controllers(self, occupied_slots):
        for i, led in enumerate(self.leds_vertes):
            try:
                if occupied_slots.get(i + 1): led.on()
                else: led.off()
            except: pass

    def set_rgb(self, r, g, b):
        if self.rgb:
            try: self.rgb.color = (r, g, b)
            except: pass

# Instance unique
gpio_manager = GPIOManager()
