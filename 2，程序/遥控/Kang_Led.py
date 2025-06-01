import machine
import time

class Led():
    def __init__(self, pin=12):  #12, 13
        self.led_pin = machine.Pin(pin)
        self.led_pin.init(mode=machine.Pin.OUT)
    def on(self):
        self.led_pin.value(1)
    def off(self):
        self.led_pin.value(0)
    def _blink(self, count, on_delay_s, off_delay_s):
        for i in range(0, count):
            self.led_pin.value(1)
            time.sleep(on_delay_s)
            self.led_pin.value(0)
            time.sleep(off_delay_s)
    def blink(self):
        self._blink(5, 0.2, 0.2)

#Led1 = Led(12)
#Led2 = Led(13)
class Led_L():
    def __init__(self):  #12, 13
        self.led_pin = machine.Pin(13)
        self.led_pin.init(mode=machine.Pin.OUT)
    def on(self):
        self.led_pin.value(1)
    def off(self):
        self.led_pin.value(0)
    def _blink(self, count, on_delay_s, off_delay_s):
        for i in range(0, count):
            self.led_pin.value(1)
            time.sleep(on_delay_s)
            self.led_pin.value(0)
            time.sleep(off_delay_s)
    def blink(self):
        self._blink(5, 0.2, 0.2)

class Led_R():
    def __init__(self):  #12, 13
        self.led_pin = machine.Pin(12)
        self.led_pin.init(mode=machine.Pin.OUT)
    def on(self):
        self.led_pin.value(1)
    def off(self):
        self.led_pin.value(0)
    def _blink(self, count, on_delay_s, off_delay_s):
        for i in range(0, count):
            self.led_pin.value(1)
            time.sleep(on_delay_s)
            self.led_pin.value(0)
            time.sleep(off_delay_s)
    def blink(self):
        self._blink(5, 0.2, 0.2)

if __name__ == "__main__":
    led=Led_R()
    led.blink()
    #led.on()
    
