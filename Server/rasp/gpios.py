from gpiozero import RGBLED, LED, Button
import threading
import time

class GPIOManager:
    def __init__(self):
        # 1. Configuration des LEDs Vertes (GPIO 27, 17, 3, 2)
        self.leds_vertes = [LED(27), LED(17), LED(3), LED(2)]

        # 2. Configuration de la LED RGB (Anode Commune)
        # Ordre : R=16, G=20, B=21 | active_high=False pour l'Anode Commune
        self.rgb = RGBLED(red=16, green=20, blue=21, active_high=False)

        # 3. Configuration du Bouton
        # bounce_time=0.1 ignore les signaux de moins de 100ms
        self.bouton = Button(13, pull_up=False, bounce_time=0.1)
        self.bouton.when_pressed = self._on_button_pressed

        self._blink_thread = None
        self._stop_blink = threading.Event()

    def _on_button_pressed(self):
        print("Bouton physique pressé !")
        self.flash_all()

    def all_off(self):
        self.stop_blink()
        for led in self.leds_vertes:
            led.off()
        self.rgb.off()

    def flash_all(self, duration=1):
        """Allume tout brièvement."""
        self.rgb.color = (1, 1, 1)
        for led in self.leds_vertes:
            led.on()
        
        def _off():
            time.sleep(duration)
            self.all_off()
        
        threading.Thread(target=_off, daemon=True).start()

    def blink_start_sequence(self):
        """Lance une séquence de clignotement pour le démarrage d'un jeu."""
        self.stop_blink()
        self._stop_blink.clear()
        self._blink_thread = threading.Thread(target=self._blink_loop, daemon=True)
        self._blink_thread.start()

    def _blink_loop(self):
        for _ in range(6): # 3 éclats
            if self._stop_blink.is_set():
                break
            for led in self.leds_vertes:
                led.toggle()
            self.rgb.color = (1, 0.5, 0) if self.leds_vertes[0].is_active else (0, 0, 0)
            time.sleep(0.2)
        self.all_off()

    def stop_blink(self):
        self._stop_blink.set()
        if self._blink_thread:
            self._blink_thread.join(timeout=0.1)

    def update_controllers(self, occupied_slots):
        """
        Allume les LEDs vertes correspondant aux slots occupés.
        occupied_slots: dict {1: sid, 2: sid, ...}
        """
        for i, led in enumerate(self.leds_vertes):
            slot_id = i + 1
            if occupied_slots.get(slot_id):
                led.on()
            else:
                led.off()

    def set_led(self, index, state):
        """Contrôle individuel d'une LED verte (0-3)."""
        if 0 <= index < len(self.leds_vertes):
            if state:
                self.leds_vertes[index].on()
            else:
                self.leds_vertes[index].off()

    def set_rgb(self, r, g, b):
        """Contrôle de la LED RGB (0-1 pour chaque canal)."""
        self.rgb.color = (r, g, b)

# Instance unique pour être partagée
try:
    gpio_manager = GPIOManager()
except Exception as e:
    print(f"Erreur d'initialisation GPIO: {e}")
    # Fallback pour environnement sans GPIO (ex: PC de dev)
    class DummyGPIO:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    gpio_manager = DummyGPIO()

if __name__ == "__main__":
    # Test si lancé directement
    print("Test GPIO Manager...")
    gpio_manager.blink_start_sequence()
    time.sleep(2)
    gpio_manager.update_controllers({1: "test", 3: "test"})
    time.sleep(2)
    gpio_manager.all_off()
