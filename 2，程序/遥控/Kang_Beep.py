import time
from machine import Pin, PWM

class Beep():
    def __init__(self, pin=10):  #10
        # 定义无源蜂鸣器 PWM 控制对象
        self.buzzer = PWM(Pin(pin, Pin.OUT))
        # 定义音符对应频率
        self.tone_list = [262, 294, 330, 350, 393, 441, 495]      
        self.buzzer.duty(0)
        self.beep_flag = 0
        
    def _didi(self, time_ms, freq=6):
        if freq<0: freq=0
        if freq>6: freq=6
        # 初始化音符频率
        tone = self.tone_list[freq]
        self.buzzer.freq(tone)
        self.buzzer.duty(512)
        time.sleep_ms(time_ms)
        self.buzzer.duty(0)
    '''
    def didi(self):
        self.buzzer.freq(350)
        self.buzzer.duty(512)
    '''
    def didi_stop(self):
        #self.buzzer.freq(350)
        self.buzzer.duty(0)
    def didi(self):
        self._didi(3000)
    def didi_0(self):
        self._didi(100, 0)
            
if __name__ == "__main__":
    beep=Beep()
    beep.didi()

