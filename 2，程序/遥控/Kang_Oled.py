from machine import Pin, ADC
#from machine import Timer
from machine import SoftI2C
from Kang_Ssd1306 import SSD1306_I2C
import time

class Oled():
    def __init__(self, scl=Pin(6),sda=Pin(7)):
        # I2C and OLED
        self.i2c = SoftI2C(sda=sda, scl=scl)
        # 创建SSD1306对象，设置显示屏尺寸为128x64
        self.display = SSD1306_I2C(128, 64, self.i2c)
        self.display_clear()
        #self._text_logo()
        
    def display_clear(self):
        self.display.fill(0)
    
    def text_welcome(self):
        line_1 = "Welcom!"
        line_2 = "Charge:click X"
        line_3 = "Remote:duble X"
        self.display.text(line_1, 35, 10, 1)
        self.display.text(line_2, 6, 30, 1)
        self.display.text(line_3, 6, 45, 1)
        
    def text_joysticks(self, joysticks): #Dict
        #joysticks_list = joysticks_str.split()
        s0="Thr:"+str(joysticks['Thr'])
        s1="Yaw:"+str(joysticks["Yaw"])
        s2="Rol:"+str(joysticks['Rol'])
        s3="Pit:"+str(joysticks['Pit'])
        self.display.text(s0, 0, 20, 1)
        self.display.text(s1, 0, 30, 1)
        self.display.text(s2, 64, 30, 1)
        self.display.text(s3, 64, 20, 1)
    def text_joysticks_aux(self, joysticks_aux):
        s1="Ya:"+str(joysticks_aux["Yaux"])
        s2="Ra:"+str(joysticks_aux['Raux'])
        s3="Pa:"+str(joysticks_aux['Paux'])
        self.display.text(s1, 0, 30, 1)
        self.display.text(s2, 72, 30, 1)
        self.display.text(s3, 72, 20, 1)
        
    def text_rc_bat(self, rc_bat):
        s = "RC:"+str(int(rc_bat))+'%'
        #print(s)
        self.display.text(s, 0, 0, 1)         
    def text_fc_bat(self, fc_bat):
        s = "FC:"+str(fc_bat)+'%'
        #print(s)
        self.display.text(s, 0,10, 1) 
    def text_fc_height(self, height):
        s = "H:"+str(height)   #Elevation
        self.display.text(s, 0, 50, 1)
    def text_fc_temp(self, temp):
        s = "T:"+str(temp)+'C'   #Temp
        self.display.text(s, 64, 50, 1)
    def text_lock(self, T_F):
        #print("lock",type(T_F))
        if T_F==1:   # True or 1
            self.display.text("Lock", 64, 10, 1)
        else:
            self.display.text("Unlock", 64, 10, 1)
    def text_finetune(self, T_F):
        if T_F==1:
            self.display.text("FT:1", 64, 0, 1)
        else:
            self.display.text("FT:0", 64, 0, 1)
    def text_fix_height(self, T_F):
        if T_F==1:   # True or 1
            self.display.text("Fix:1", 64, 40, 1)
        else:
            self.display.text("Fix:0", 64, 40, 1)
    def text_use_imu(self, T_F):
        if T_F==1:   # True or 1
            self.display.text("IMU:1", 0, 40, 1) # Flight Cobtroller
        else:
            self.display.text("IMU:0", 0, 40, 1)
            
    def text_menu_select_charge(self):
        self.display.text("mode0: Charge", 0, 28, 1) # 显示在屏幕中间
    def text_menu_select_control(self):
        self.display.text("mode1: Control", 0, 28, 1) # 显示在屏幕中间
    def text_FC_battery_low(self):
        self.display.text("FC battery low!", 0, 40, 1) # 显示在屏幕中间
    def text_RC_battery_low(self):
        self.display.text("RC battery low!", 0, 30, 1) # 显示在屏幕中间
    def text_logo(self):
        # max row is 64 ,chinese char needs 16*16 pixle
        self.display.text("Little Goal Tech!!! ", 0, 56, 1)
    def display_show(self):
        self.display.show()
    def poweroff(self):
        display.poweroff()
    def display_RC_data_simple(self, joysticks, rc_bat, lock, fc_bat=-100, fc_height=-100):
        self.display_clear()
        #self.text_joysticks_str(joysticks)
        self.text_joysticks_list(joysticks)
        self.text_rc_bat(rc_bat) #0~100
        self.text_lock(lock) #0~100
        if fc_bat!=-100 and fc_height!=-100:
            self.text_fc_bat(fc_bat)
            s = "Elevation:"+str(fc_height)+'M'   #Elevation
            self.display.text(s, 0, 40, 1)
        self.text_logo()
        self.display_show()
        
    def display_RC_data(self, joysticks, rc_bat, key_command):
        self.display_clear()
        #self.text_joysticks_str(joysticks)
        self.text_joysticks(joysticks)
        self.text_rc_bat(rc_bat) #0~100
        self.text_lock(key_command["Lock"])
        self.text_fix_height(key_command["Fix"])
        self.text_finetune(key_command['finetune'])
        self.text_use_imu(key_command['Imu'])
        self.display_show()
    def display_RC_FC_data(self, joysticks, rc_bat, fc_data, key_command):
        self.display_clear()
        #self.text_joysticks_str(joysticks)
        self.text_joysticks(joysticks)
        self.text_rc_bat(rc_bat) #0~100
        self.text_fc_height(fc_data['fc_height'])   
        self.text_fc_bat(fc_data['fc_bat'])
        self.text_fc_temp(fc_data['fc_temp'])
        self.text_lock(key_command["Lock"])
        self.text_fix_height(key_command["Fix"])
        self.text_finetune(key_command['finetune'])
        self.text_use_imu(key_command['Imu'])
        self.display_show()
    def display_RCaux_data(self, joysticks_aux, rc_bat, key_command):
        self.display_clear()
        self.text_joysticks_aux(joysticks_aux)
        self.text_rc_bat(rc_bat) #0~100
        self.text_lock(key_command["Lock"])
        self.text_fix_height(key_command["Fix"])
        self.text_finetune(key_command['finetune'])
        self.text_use_imu(key_command['Imu'])
        self.display_show()
    def display_RCaux_FC_data(self, joysticks_aux, rc_bat,fc_data, key_command):
        self.display_clear()
        self.text_joysticks_aux(joysticks_aux)
        self.text_rc_bat(rc_bat) #0~100
        self.text_fc_height(fc_data['fc_height'])   
        self.text_fc_bat(fc_data['fc_bat'])
        self.text_fc_temp(fc_data['fc_temp'])
        self.text_lock(key_command["Lock"])
        self.text_fix_height(key_command["Fix"])
        self.text_finetune(key_command['finetune'])
        self.text_use_imu(key_command['Imu'])
        self.display_show()
        
        
if __name__ == "__main__":
    oled = Oled()
    for i in range(0,100):
        oled.display_clear()
        oled.text_rc_bat(i)
        oled.text_fc_bat(i)
        #print(i)
        oled.text_fight_height(i)
        oled.text_logo()
        oled.text_joysticks(i, i, i,i)
        oled.display_show()
        time.sleep(0.05) #default 20times/second
    

            
