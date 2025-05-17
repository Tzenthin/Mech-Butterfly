from machine import PWM, Pin
import math


class Servo:
    """
    A simple class for controlling hobby servos.
    Args:
        pin (machine.Pin): The pin where servo is connected. Must support PWM.
        freq (int): The frequency of the signal, in hertz.
        min_us (int): The minimum signal length supported by the servo.
        max_us (int): The maximum signal length supported by the servo.
        angle (int): The angle between the minimum and maximum positions.
    """
    def __init__(self, pwm_pin, volt_pin=8, volt_level=0, freq=50, min_us=500, max_us=2500, angle=180):
        self.min_us = min_us
        self.max_us = max_us
        self.us = 0
        self.freq = freq
        self.angle = angle
        self.pwm = PWM(Pin(pwm_pin), freq=freq, duty=0)
        self.volt_select = Pin(volt_pin)
        self.volt_select.init(mode=Pin.OUT)
        #默认选择低电压给舵机供电，也就是1S电池电压
        self.set_servo_volt_low()
    
    #选择使用升压后的电压给舵机供电
    def set_servo_volt_high(self):
        self.volt_select.value(1)
    def set_servo_volt_low(self):
        self.volt_select.value(0)
    
    def write_us(self, us):
        """Set the signal to be ``us`` microseconds long. Zero disables it."""
        if us == 0:
            self.pwm.duty(0)
            return
        us = min(self.max_us, max(self.min_us, us))
        duty = us * 1024 * self.freq // 1000000
        self.pwm.duty(duty)

    def write_angle(self, degrees=None, radians=None):
        """Move to the specified angle in ``degrees`` or ``radians``."""
        if degrees is None:
            degrees = math.degrees(radians)
        degrees = degrees % 360
        total_range = self.max_us - self.min_us
        us = self.min_us + total_range * degrees // self.angle
        self.write_us(us)




if __name__ == '__main__':
    #servo1 = Servo(3, 6)
    servo1 = Servo(4)
    #servo1.set_servo_volt_high()
    servo1.write_angle(10)  
