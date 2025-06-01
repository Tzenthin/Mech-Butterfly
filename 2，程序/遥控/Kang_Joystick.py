import time
from machine import Pin, ADC
#from machine import Timer
#import machine
from Kang_Queue import Queue

class Joystick():
    def __init__(self, pin=0): #0:thr 1:yaw 2:roll 3:picth
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)  #开启衰减，量程增大到3.3V
        self.adc_offset = 0
        self.offset_cnt = 200
        self.smoothed_last = 0
        #self.temp = []
        self.adc_average_counter = 0
        self.adc_average_time = 5
        self.use_low_pass = True
        self.alpha = 0.1  #low pass coff
        self.queue = Queue()
        #self._offset()
        #assert 0==1
    def _offset(self):
        adc_sum = 0
        #time.sleep_ms(1)
        for i in range(self.offset_cnt):
            adc_value = self.adc.read() #* 3.3 / 4095
            adc_sum += adc_value
            time.sleep_ms(1)
            if i >= self.offset_cnt - self.adc_average_time:
                #self.temp.append(adc_value)
                self.queue.enqueue(adc_value)
        self.smoothed_last = adc_sum//self.offset_cnt
        self.adc_offset = self.smoothed_last/4.096 - 500 # - 4096//2
        #print("offset : ", self.adc_offset)
        #return
        
    
    def _low_pass_smooth(self, average_adc):
        smoothed_last = int(self.alpha*self.smoothed_last + (1-self.alpha)*average_adc)
        return smoothed_last
    
    def _data_smooth(self, adc_value):
        self.queue.dequeue()
        self.queue.enqueue(adc_value)
        average_adc = self.queue.average()
        if self.use_low_pass:   
            self.smoothed_last = self._low_pass_smooth(average_adc)
            return self.smoothed_last
        else:
            return average_adc 
    
    def normalization(self, adc_raw_data):
        normalized_data = round((adc_raw_data/4.096 - self.adc_offset))   # 0~1000
        if normalized_data<0: normalized_data=0
        if normalized_data>1000: normalized_data=1000
        return normalized_data

    
    def joystick_read_data(self):
        adc_value = self.adc.read() #* 3.3 / 4095
        adc_result = self._data_smooth(adc_value)
        #print(smoothed_adc_last)
        #if adc_result != None:
        adc_result = self.normalization(adc_result)
            #smoothed_adc_last = ' '.join(smoothed_adc_last)
            #adc_result = [str(adc_result[0]), str(adc_result[1]), \
            #              str(adc_result[2]),str(adc_result[3]), str(adc_result[4])]
            #print(smoothed_adc_last)
            #assert 0==1
        return adc_result
    
    
class Joysticks():
    def __init__(self): #0:thr 1:yaw 2:roll 3:picth
        self.joy_thr = Joystick(0)
        self.joy_yaw = Joystick(1)
        self.joy_rol = Joystick(2)
        self.joy_pit = Joystick(3)
    def read_data(self):
        thr_data = self.joy_thr.joystick_read_data()
        yaw_data = self.joy_yaw.joystick_read_data()
        rol_data = self.joy_rol.joystick_read_data()
        pit_data = self.joy_pit.joystick_read_data()
        #joysticks_data = ' '.join([str(thr_data), str(yaw_data),str(rol_data), str(pit_data)])
        joysticks_data = {'Thr':thr_data, 'Yaw':yaw_data, 'Rol':rol_data, 'Pit':pit_data} #[thr_data, yaw_data, rol_data, pit_data]
        return joysticks_data



#将0~1000的绝对量，映射到-0.1~0.1的增量
def Absolute_to_Relative(data):  
    data = (data-500)/500
    return data
    

if __name__ == "__main__":
    joy = Joystick(pin=2)
    J = Joysticks()
    J.joy_yaw._offset()
    while True:
        #adc_data = joy.joystick_read_data()
        adc_data = J.read_data()
        if adc_data != None:
            print(adc_data)
        time.sleep(0.01)