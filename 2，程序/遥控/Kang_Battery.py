import time
from machine import Pin, ADC
#from machine import Timer
#import machine
from Kang_Queue import Queue

class Battery():
    def __init__(self, pin=4):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)  #开启衰减，量程增大到3.3V
        self.adc_offset = 0
        self.offset_cnt = 100
        self.smoothed_last = 0
        self.temp = []
        self.adc_average_counter = 0
        self.adc_average_time = 5
        self.use_low_pass = True
        self.alpha = 0.97  #low pass coff
        self.queue = Queue()
        self._offset()
        #assert 0==1
        
    def _offset(self):
        adc_sum = 0
        for i in range(self.offset_cnt):
            adc_value = self.adc.read() #* 3.3 / 4095
            adc_sum += adc_value
            if i >= self.offset_cnt - self.adc_average_time:
                #self.temp.append(adc_value)
                self.queue.enqueue(adc_value)
        self.smoothed_last = adc_sum//self.offset_cnt
        #self.adc_offset = self.smoothed_last #- 4095//2
        #print("offset : ", self.adc_offset)
        #return
        
    def _calibration(self, V_sample):
        #V_cal = 0.868*V_sample + 0.09
        V_cal = 0.8*V_sample + 0.23
        return V_cal
    
    def _low_pass_smooth(self, average_adc):
        smoothed_last = int(self.alpha*self.smoothed_last + (1-self.alpha)*average_adc)
        return smoothed_last
    
    def data_smooth(self, adc_value):
        #self.temp[self.adc_average_counter] = adc_value
        self.queue.dequeue()
        self.queue.enqueue(adc_value)
        average_adc = self.queue.average()
        if self.use_low_pass:   
            self.smoothed_last = self._low_pass_smooth(average_adc)
            return self.smoothed_last
        else:
            return average_adc         
        '''
        if self.adc_average_counter==self.adc_average_time-1:
            average_adc = sum(self.temp)//self.adc_average_time   
            self.adc_average_counter = 0
            if self.use_low_pass:   
                self.smoothed_last = self.low_pass_smooth(average_adc)
                return self.smoothed_last
            else:
                return average_adc 
        else: 
            self.adc_average_counter += 1
            return self.smoothed_last'''
    
    def normalization(self, adc_raw_data):  # input: 0~4096
        Volt_min = 3.3
        Volt_max = 4.2
        normalized_data = (adc_raw_data-self.adc_offset)*3.3/4096   # 0~3.3
        # recording to the real circuit, plus 2 is the real battery voltage
        sample_volt = normalized_data*2  
        cal_volt = self._calibration(sample_volt)
        #print(cal_volt)
        percent = int((cal_volt-Volt_min)/(Volt_max-Volt_min)*100)  # 0~100
        #if normalized_data<0: normalized_data=0
        #if normalized_data>1000: normalized_data=1000
        return cal_volt, percent

    
    def battery_read_remaining(self):
        adc_value = self.adc.read() #* 3.3 / 4095
        adc_result = self.data_smooth(adc_value)
        volt_result, percent_result = self.normalization(adc_result)
        return volt_result, percent_result



if __name__ == "__main__":
    bat = Battery(4)
    while True:
        adc_data = bat.battery_read_remaining()
        if adc_data != None:
            print(adc_data)
        time.sleep(0.01)
