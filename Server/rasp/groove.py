from gpiozero import OutputDevice
import time

class GroveChainableLED:
    def _init_(self, clk_pin, data_pin, num_leds=1):
        self.clk = OutputDevice(clk_pin)
        self.data = OutputDevice(data_pin)
        self.num_leds = num_leds

    def _send_byte(self, b):
        # Ensure we are only dealing with 8 bits
        for i in range(8):
            # Check the most significant bit (MSB)
            if (b & 0x80):
                self.data.on()
            else:
                self.data.off()
            
            self.clk.on()
            # P9813 is fast, but GPIO overhead in Python is usually enough. 
            # We keep micro-delays for safety on faster Pi models.
            # time.sleep(0.000001) 
            self.clk.off()
            b = (b << 1) & 0xFF # Shift and mask to keep it 8-bit

    def _send_color(self, r, g, b):
        # P9813 Checksum: 11 (inverted B7-6) (inverted G7-6) (inverted R7-6)
        checksum = 0xC0
        if (b & 0x80) == 0: checksum |= 0x20
        if (b & 0x40) == 0: checksum |= 0x10
        if (g & 0x80) == 0: checksum |= 0x08
        if (g & 0x40) == 0: checksum |= 0x04
        if (r & 0x80) == 0: checksum |= 0x02
        if (r & 0x40) == 0: checksum |= 0x01
        
        self._send_byte(checksum)
        self._send_byte(b)
        self._send_byte(g)
        self._send_byte(r)

    def set_color(self, r, g, b):
        # Start Frame: 32 bits of zeros
        for _ in range(4): 
            self._send_byte(0)
        
        # Send color for every LED in the chain
        for _ in range(self.num_leds):
            self._send_color(r, g, b)
            
        # End Frame: 32 bits of zeros
        for _ in range(4): 
            self._send_byte(0)

# --- Main Program ---
led = GroveChainableLED(clk_pin=18, data_pin=23)

try:
    while True:
        led.set_color(255, 0, 0) # Red
        time.sleep(1)
        led.set_color(0, 255, 0) # Green
        time.sleep(1)
        led.set_color(0, 0, 255) # Blue
        time.sleep(1)
except KeyboardInterrupt:
    led.set_color(0, 0, 0)