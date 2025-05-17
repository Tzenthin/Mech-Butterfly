import time
#import math
import json
from Kang_Espnow_FC import Esp_Comm_FC
from Kang_Sevor import Servo

from Kang_Battery import Battery
from Kang_Led import Led

from Kang_Utils import map_range

import math


class Ornithopter():
    def __init__(self): #FixedWing_Type  0:伞翼机，不给开飞控； 1：手抛飞机：可选择是否开飞控
        self.bat = Battery()
        #self.led=Led()
        
        #PWM3控制着
        self.servo_left = Servo(pwm_pin=4)
        #self.servo_left.set_servo_volt_high()
        #选择舵机的供电电压，high则启用升压模块，使用6V供电，low直接使用1S电池供电
        #PWM4控制偏航或者横滚
        self.servo_right = Servo(pwm_pin=5)  # 根据硬件的IO口连接配置
        #self.servo_right.set_servo_volt_high()
        
        #需要用到的变量初始化
        self.fly_flag = 0  #飞行标志
        self.flight_height = 0 #飞行高度
        #定高标志
        self.height_fixed = 0
        self.target_altitude = 0
        self.init_pitch_angle = 90
        self.init_roll_angle = 90
        
        self.left_middle_position = 90  #初始角度为90度，使用的角度范围是30~150，共120度
        self.right_middle_position = 90
        '''
        self.diffrential = 0
        self.up_down= 0
        self.amplitude = 0
        self.servo_delay = 10 #用延时控制舵机的打舵速度 单位ms
        '''
    def add_peer(self, peer_mac):
        self.espnow_fc = Esp_Comm_FC(peer_mac)
        

        
    def start(self): 
        self.led.blink()
        self.led.off()
        #MPU校准
        self.mpu6050_calibration(self.cali_cnt)
        #BMP280高度标定校准
        self.altitude_offset = self.bmp280_altitude_calibration()
        self.led.on()


    def fly_loop(self):
        i=0
        while True:
            i+=1
            if i>1000: i=0
            altitude = 0#self.bmp.read_altitude()
            altitude = 0#round(altitude-self.altitude_offset, 1) #保留一位小数
            temperature = 0#round(self.bmp.temperature, 1) #保留一位小数
            
            if self.fly_flag==0:
                bat_data = self.bat.battery_read_remaining()

            if i%50==0:
                send_data = json.dumps({"fc_bat":round(bat_data[0], 1), "fc_height":altitude, "fc_temp": temperature})
                #print(send_data)
                self.espnow_fc.send(send_data) 
            
            #servo_delay, amplitude, diffrential, up_down, lock = recv_data(esp_now_fc)
            #motor_servo_control(motor, esp_now_fc.thr, servo, mapping_servo_angle(esp_now_fc.yaw))

            # 获取遥控器发来的数据
            rc_thr_width = self.espnow_fc.rc_thr 
            servo_delay = map_range(rc_thr_width, 0, 1000, 16, 8) #油门代表扑动频率快慢，用于延时8ms~12ms,单位ms
            diffrential = map_range(self.espnow_fc.rc_rol, 0, 1000, -20, 20) #roll 实现转向
            up_down = map_range(self.espnow_fc.rc_pit, 0, 1000, -20, 20) #roll 实现俯仰动作
            amplitude = map_range(self.espnow_fc.rc_yaw, 0, 1000, 40, 90)
            left_error = map_range(self.espnow_fc.rc_rol_aux, -200,200, -20, 20)
            right_error = map_range(self.espnow_fc.rc_pit_aux, -200,200, -20, 20) 
            #print(rc_thr_width, rc_rol_width, rc_pit_width, rc_yaw_width)
            #print("lock imu fix ", esp_now_fc.rc_lock, esp_now_fc.rc_imu, esp_now_fc.rc_fix)
            #print("r_aux p_aux y_aux", esp_now_fc.rc_rol_aux, esp_now_fc.rc_pit_aux, esp_now_fc.rc_yaw_aux)
            
            # 根据遥控器的上锁指令,以及油门大小判断飞行标志
            if rc_thr_width>100:
                self.fly_flag = 1 - self.espnow_fc.rc_lock
            else:
                self.fly_flag = 0
            
            if self.fly_flag == 1:
                #self.led.off()
                for i in range(0, 180, 9):
                    left_angle = (self.left_middle_position + left_error + up_down) + (amplitude-diffrential)*math.cos(i/180*math.pi)
                    right_angle =(self.right_middle_position- right_error- up_down) - (amplitude+diffrential)*math.cos(i/180*math.pi)
                    left_angle = min(180, max(left_angle, 0))
                    right_angle = min(180, max(right_angle, 0))
                    self.servo_left.write_angle(int(left_angle))
                    self.servo_right.write_angle(int(right_angle))
                    time.sleep_ms(int(servo_delay))
                    #print(left_angle, right_angle)
                for i in range(180, 0, -9):
                    left_angle = (self.left_middle_position + left_error + up_down) + (amplitude-diffrential)*math.cos(i/180*math.pi)
                    right_angle =(self.right_middle_position- right_error- up_down) - (amplitude+diffrential)*math.cos(i/180*math.pi)
                    left_angle = min(180, max(left_angle, 0))
                    right_angle = min(180, max(right_angle, 0))
                    self.servo_left.write_angle(int(left_angle))
                    self.servo_right.write_angle(int(right_angle))
                    time.sleep_ms(int(servo_delay))
                    #print(left_angle, right_angle)
            else:
                #self.led.on()
                self.servo_left.write_angle(int(self.left_middle_position + left_error))
                self.servo_right.write_angle(int(self.right_middle_position- right_error))
                time.sleep_ms(int(servo_delay))
                
                
            


    def bmp280_altitude_calibration(self):
        alt_sum = 0
        cal_cnt = 5
        for i in range(cal_cnt):
            #pressure=bmp.pressure
            #p_bar=pressure/100000
            #p_mmHg=pressure/133.3224
            #temperature=bmp.temperature
            #print("Temperature: {} C".format(temperature))
            #print("Pressure: {} Pa, {} bar, {} mmHg".format(pressure,p_bar,p_mmHg))
            alt = self.bmp.read_altitude()
            alt_sum += alt
            #print(alt)
            time.sleep(0.1)
        altitude = alt_sum/cal_cnt
        return altitude



