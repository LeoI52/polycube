from gpiozero import OutputDevice
import time

class GroveChainableLED:
    def _init_(self, clk_pin, data_pin, num_leds=1):
        self.clk = OutputDevice(clk_pin)
        self.data = OutputDevice(data_pin)
        self.num_leds = num_leds

    def _send_byte(self, b):
        for i in range(8):
            # Send MSB first
            if (b & 0x80) != 0:
                self.data.on()
            else:
                self.data.off()
            self.clk.on()
            b <<= 1
            self.clk.off()

    def _send_color(self, r, g, b):
        # The P9813 expects a 32-bit packet per LED:
        # [Checksum][Blue][Green][Red]
        # Checksum is the inverted XOR of the 2 high bits of B, G, and R
        checksum = 0xC0 # Start with 11000000
        checksum |= (0x3F & ~( (b & 0xC0) >> 2 | (g & 0xC0) >> 4 | (r & 0xC0) >> 6 ))
        
        self._send_byte(checksum)
        self._send_byte(b)
        self._send_byte(g)
        self._send_byte(r)

    def set_color(self, led_index, r, g, b):
        # Start Frame (32 zeros)
        for _ in range(4): self._send_byte(0)
        
        # Data for each LED
        for _ in range(self.num_leds):
            self._send_color(r, g, b)
            
        # End Frame (32 zeros)
        for _ in range(4): self._send_byte(0)

# Initialize on GPIO 18 (Clock) and GPIO 23 (Data)
led = GroveChainableLED(clk_pin=18, data_pin=23)

print("Cycling colors... Press Ctrl+C to stop.")

try:
    while True:
        print("Red")
        led.set_color(0, 255, 0, 0)
        time.sleep(1)
        print("Green")
        led.set_color(0, 0, 255, 0)
        time.sleep(1)
        print("Blue")
        led.set_color(0, 0, 0, 255)
        time.sleep(1)
except KeyboardInterrupt:
    led.set_color(0, 0, 0, 0) # Turn off
    print("\nDone.")