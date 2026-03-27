from gpiozero import OutputDevice
import time

class GroveChainableLED:
    # This MUST be indented exactly one level (4 spaces)
    def _init_(self, clk_pin, data_pin, num_leds=1):
        self.clk = OutputDevice(clk_pin)
        self.data = OutputDevice(data_pin)
        self.num_leds = num_leds

    def _send_byte(self, b):
        for i in range(8):
            if (b & 0x80) != 0:
                self.data.on()
            else:
                self.data.off()
            self.clk.on()
            # Added a tiny delay for signal stability
            time.sleep(0.0001)
            self.clk.off()
            time.sleep(0.0001)
            b <<= 1

    def _send_color(self, r, g, b):
        checksum = 0xC0
        checksum |= (0x3F & ~( (b & 0xC0) >> 2 | (g & 0xC0) >> 4 | (r & 0xC0) >> 6 ))
        self._send_byte(checksum)
        self._send_byte(b)
        self._send_byte(g)
        self._send_byte(r)

    def set_color(self, r, g, b):
        # Start Frame
        for _ in range(4): self._send_byte(0)
        # Data
        for _ in range(self.num_leds):
            self._send_color(r, g, b)
        # End Frame
        for _ in range(4): self._send_byte(0)

# --- Main Program (Outside the class) ---
led = GroveChainableLED(clk_pin=18, data_pin=23)

try:
    while True:
        print("Red")
        led.set_color(255, 0, 0)
        time.sleep(1)
        print("Green")
        led.set_color(0, 255, 0)
        time.sleep(1)
        print("Blue")
        led.set_color(0, 0, 255)
        time.sleep(1)
except KeyboardInterrupt:
    led.set_color(0, 0, 0)
    print("\nStopped.")