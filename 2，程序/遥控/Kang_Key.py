import time
from machine import Pin

from Kang_Led import Led

class Key():
    def __init__(self, pin):  #X:9, B:5, Y:12, A:13
        # 创建按键输入引脚类，如果引脚的一端接 Vcc，则设置下拉电阻；如果一端接的是 GND，则配置上拉电阻。
        self.pin = pin
        self.button = Pin(self.pin, Pin.IN, Pin.PULL_UP)  #34 35 36 40  Pin.PULL_DOWN
        self.press_flag=0
        self.press_count = 0
        self.button.irq(self.button_interrupt_handler, Pin.IRQ_FALLING)
        '''
        self.mode = 0  #0:充电 1：遥控
        self.lock = 1  #0:解锁  1：上锁
        self.fix_height = 0 #0:不定高 1：定高
        self.finetune = 0   #0:不微调 1：微调
        '''
    # 定义中断处理函数
    def button_interrupt_handler(self, temp):
        # 先用软件进行消抖
        time.sleep_ms(10)
        if self.button.value()==0:
            self.press_count += 1
            self.press_flag = 1  #在外部处理完相关任务之后，手动改变该标志位为0
            self.mode = self.press_count % 2
        
        #print("Button pressed!")
        #print(self.press_flag)


class KeyA():
    def __init__(self, pin=13):
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)  #34 35 36 40  Pin.PULL_DOWN
        self.press_flag=0
        self.press_count = 1
        self.lock = 1  #0 解锁: 1：上锁
        self.button.irq(self.button_interrupt_handler, Pin.IRQ_FALLING)
    # 定义中断处理函数
    def button_interrupt_handler(self, temp):
        time.sleep_ms(10)
        if self.button.value()==0:
            self.press_count += 1
            self.press_flag = 1  #在外部处理完相关任务之后，手动改变该标志位为0
            self.lock = self.press_count % 2
        
class KeyB():
    def __init__(self, pin=5):
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)  #34 35 36 40  Pin.PULL_DOWN
        self.press_flag=0
        self.press_count = 0
        self.fix_height = 0  #0:不定高飞行 1：定高状态
        self.button.irq(self.button_interrupt_handler, Pin.IRQ_FALLING)
    # 定义中断处理函数
    def button_interrupt_handler(self, temp):
        time.sleep_ms(10)
        if self.button.value()==0:
            self.press_count += 1
            self.press_flag = 1  #在外部处理完相关任务之后，手动改变该标志位为0
            self.fix_height = self.press_count % 2

class KeyX():
    def __init__(self, pin=9):
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)  #34 35 36 40  Pin.PULL_DOWN
        self.press_flag=0
        #self.press_count = 0
        self.mode = 0  #0:充电sleep低功耗模式 1：遥控模式
        self.double_click = 0
        self.click = 0
        self.click_time = 0 #time.tick_ms()
        self.imu = 0
        self.button.irq(self.button_interrupt_handler, Pin.IRQ_FALLING)
    # 定义中断处理函数
    def button_interrupt_handler(self, temp):
        time.sleep_ms(10)
        if self.button.value()==0:
            #如果用户连续按键，不止2次，此处会有bug，改怎么应对？
            if time.ticks_ms() - self.click_time<500:   #两次电机之间时间间隔小于500ms，则判断为双击
                self.double_click=1
                self.click = 0
                #self.press_count -= 1
                #self.mode = 1-self.selection #1- self.mode #self.press_count % 2
            else:
                #self.press_flag = 1 
                #self.double_click=0
                self.click = 1
                #self.selection = 1-self.selection
                #self.mode = self.press_count % 2
                self.click_time = time.ticks_ms()
                self.imu = 1-self.imu
        
        
        
class KeyY():
    def __init__(self, pin=12):
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)  #34 35 36 40  Pin.PULL_DOWN
        self.press_flag=0
        self.press_count = 0
        self.finetune = 0  #0:不微调 1：微调
        self.button.irq(self.button_interrupt_handler, Pin.IRQ_FALLING)
    # 定义中断处理函数
    def button_interrupt_handler(self, temp):
        time.sleep_ms(10)
        if self.button.value()==0:
            self.press_count += 1
            self.press_flag = 1  #在外部处理完相关任务之后，手动改变该标志位为0
            self.finetune = self.press_count % 2        
        
class Keys():
    """
        #按键功能说明：
        # X:睡眠和遥控功能选择  0:充电 1：遥控
        # Y:飞行前的yaw pit rol 微调模式进入和退出 0：不微调  1： 微调
        # A：解锁和上锁    0:上锁  1：解锁
        # B：定高和取消定高 /取消定高后，定高前的油门会按照pid调节衰减或增加到当前油门大小，防止突然掉落   0：不定高 1： 定高
    """
    def __init__(self, pin_A=13, pin_B=5, pin_X=9, pin_Y=12):  #X:9, B:5, Y:12, A:13
        self.A = Key(pin_A)
        self.B = Key(pin_B)
        self.X = Key(pin_X)
        self.Y = Key(pin_Y)
        self.mode = self.X.press_count % 2   
        self.finetune = self.Y.press_count % 2
        self.lock = self.A.press_count % 2
        self.fix_height = self.B.press_count % 2

        
if __name__ == "__main__":
    #LED 和Keys不能同时初始化，因为12 13 IO口相同
    #led1=Led()
    key = KeyY()

    while True:
        time.sleep(1)
        
        
        if key.finetune: #key.press_count%2:
            #led1.on()
            print(1)
            
            #key1.press_flag=0
        else:
            #led1.off()
            print(0)
        #print(key1.press_count)
        
        
        '''
        if keys.X.press_count%2:  #keys.mode
            #led1.on()
            print("on")
        else:
            #led1.off()
            print('off')
        print(keys.X.press_count)
        '''
        

        