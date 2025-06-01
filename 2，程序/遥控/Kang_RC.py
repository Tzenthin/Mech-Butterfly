from Kang_Beep import Beep
from Kang_Battery import Battery
from Kang_Espnow_RC import Esp_Comm
from Kang_Joystick import Joysticks, Absolute_to_Relative
from Kang_Key import Key, KeyX, KeyY, KeyA, KeyB
from Kang_Led import Led
from Kang_Oled import Oled
import Kang_Main_Funs as funs
import time
from machine import WDT

class RC():
    def __init__(self):
        self.joysticks = Joysticks()
        self.oled = Oled()
        self.bat = Battery()
        self.beep=Beep()
        # 12 13同时也是LED的IO口，用于按键后，就不可再用于LED
        self.Key_A = KeyA()  #lock/unlock  0|1
        self.Key_B = KeyB()   #fix_height   0|1
        self.Key_X = KeyX()   #sleep/work   0|1
        self.Key_Y = KeyY()  #fine_tune    0|1
            
        #self.wdt = WDT(timeout=2000)
        #wdt.feed()
        self.min_volt = 10 #percent
        self.max_volt = 95
        
        
    def add_peer(self, peer_mac):
        self.esp_comm = Esp_Comm(peer_mac)
        
    def set_min_max_volt(self, min_volt=10, max_volt=95):
        self.min_volt = min_volt #percent
        self.max_volt = max_volt
        
    def run(self):
        
        #如果遥控器死机，设置的看门狗定时器会使其重启
        #如果飞控还在运行的，重启后的第一件事就是发送上锁的信号
        #要在最短的时间里让飞行器停止下来
        joysticks_data = {"Thr":0, "Yaw":500, "Rol":500, "Pit":500}
        joysticks_data_aux = {"Yaux":0, "Raux":0, "Paux":0}
        key_command = {"Lock":1, "Fix":0,"Imu":0 }
        for i in range(5):
            self.esp_comm.send(joysticks_data, joysticks_data_aux, key_command)
            time.sleep(0.05)
        
        '''
        #先进入sleep模式和遥控模式选择界面
        self.wait_for_mode_select()
        if self.Key_X.click==1:
            self.charging()
        '''
        
        wdt = WDT(timeout=1000)  
        # 遥控模式
        if True:#self.Key_X.double_click==1:
            
            self.joysticks.joy_yaw._offset()
            self.joysticks.joy_thr._offset()
            self.joysticks.joy_rol._offset()
            self.joysticks.joy_pit._offset()
            
            
            i=0
            joysticks_data_aux = {'Yaux':0, 'Raux':0, 'Paux':0}
            pre_joysticks_data = {'Thr':0, 'Yaw':0, 'Rol':0, 'Pit':0}  #用于记录遥杆的上一次值，在进入微调状态的时候，TYRP四个通道保持该值的发送
            while True:
                wdt.feed()
                joysticks_data = self.joysticks.read_data()   # List[thr, yaw, roll, pitch]
                #print(joysticks_data)
                bat_data = self.bat.battery_read_remaining()
                #oled.display_RC_data(joysticks_data, bat_data[1], esp_comm.fc_bat, esp_comm.flight_height)
                #如果飞控的电池没有电或者 如果遥控器的电池没有电了
                if abs(self.esp_comm.fc_data["fc_bat"])<0 or bat_data[1]<0 :
                    #print( type(abs(esp_comm.fc_data["fc_bat"])), type(bat_data[1]) )\
                    #print( abs(esp_comm.fc_data["fc_bat"]), bat_data[1])
                    joysticks_data = {"Thr":0, "Yaw":500, "Rol":500, "Pit":500}
                    joysticks_data_aux = {"Yaux":0, "Raux":0, "Paux":0}
                    key_command = {"Lock":1, "Fix":0,"Imu":0 }
                    for i in range(5):
                        self.esp_comm.send(joysticks_data, joysticks_data_aux, key_command)
                        time.sleep(0.05)
                    self.oled_display_battery_low(self.esp_comm.fc_data["fc_bat"], bat_data[1])
                    self.beep.didi()
                    
                    #i+=1
                else:
                    finetune = self.Key_Y.finetune #默认为0不微调
                    key_command = {"finetune":self.Key_Y.finetune, "Lock":self.Key_A.lock, "Fix":self.Key_B.fix_height,"Imu":self.Key_X.imu}
                    
                    #如果进入微调模式
                    if finetune:
                        joysticks_data_aux= self.get_aux(joysticks_data, joysticks_data_aux)
                        if i%10==0:  #限制发送数据，和显示数据频率
                            #如果上一次遥控指令发送正常被接收，则继续发送遥控指令
                            if self.esp_comm.succ_flag==1:
                                self.esp_comm.send(pre_joysticks_data, joysticks_data_aux, key_command)
                                self.oled.display_RCaux_FC_data(joysticks_data_aux, bat_data[1], self.esp_comm.fc_data, key_command)
                            #否则就发送初始化指令
                            else:
                                #如果正常的遥控指令发送失败，可能就是
                                #joysticks_data = {"Thr":0, "Yaw":500, "Rol":500, "Pit":500}
                                #joysticks_data_aux = {"Yaux":0, "Raux":0, "Paux":0}
                                #key_command = {"Lock":1, "Fix":0,"Imu":0 }
                                #self.esp_comm.send(pre_joysticks_data, joysticks_data_aux, key_command)
                                self.esp_comm.send({"Thr":0, "Yaw":500, "Rol":500, "Pit":500}, {"Yaux":0, "Raux":0, "Paux":0}, {"Lock":1, "Fix":0,"Imu":0 })
                                self.oled.display_RCaux_data(joysticks_data_aux, bat_data[1], key_command)
                        i+=1
                        time.sleep(0.01) #0.01*5=0.05s, 20Hz send frequency                    
                    #正常遥控采集状态
                    else:
                        #print('frekvjhbfgnvd')
                        if i%10==0:  ##限制发送数据，和显示数据频率
                            if self.esp_comm.succ_flag==1:
                                self.esp_comm.send(joysticks_data, joysticks_data_aux, key_command)
                            else:
                                self.esp_comm.send({"Thr":0, "Yaw":500, "Rol":500, "Pit":500}, {"Yaux":0, "Raux":0, "Paux":0}, {"Lock":1, "Fix":0,"Imu":0 })
                            pre_joysticks_data = joysticks_data
                            joysticks_data['Yaw'] = round(joysticks_data['Yaw']+joysticks_data_aux['Yaux'])
                            joysticks_data['Rol'] = round(joysticks_data['Rol']+joysticks_data_aux['Raux'])
                            joysticks_data['Pit'] = round(joysticks_data['Pit']+joysticks_data_aux['Paux'])
                            if self.esp_comm.succ_flag==1:
                                #disconnected_times=0
                                self.oled.display_RC_FC_data(joysticks_data, bat_data[1], self.esp_comm.fc_data, key_command)
                            else:
                                #disconnected_times += 1
                                self.oled.display_RC_data(joysticks_data, bat_data[1], key_command)
                        i+=1
                        time.sleep(0.01) #0.01*5=0.05s, 20Hz send frequency
        
        
    def wait_for_mode_select(self):
        self.oled.display_clear()
        self.oled.text_welcome()
        self.oled.display_show()
        while True:
            if self.Key_X.click: #如果双击，便退出模式选择界面，此时在class中，mode的值也已经确定了
                time.sleep(1)
                if self.Key_X.click: break
            if self.Key_X.double_click:
                break
            #因为双击时间设定为500ms内。所以，为了不在第一次击的时候就显示切换到下一个选项，这里的延时要大于500ms，才能看起来符合人的习惯
            time.sleep_ms(1000)
        
    def charging(self):
        i=0
        while True:
            bat_data = self.bat.battery_read_remaining()[1]
            time.sleep(0.1)
            if i%20==0:
                self.oled.display_clear()
                self.oled.text_rc_bat(bat_data)
                self.oled.display_show()
            i+=1
            if bat_data>self.max_volt:
                self.beep.didi()
    def oled_display_battery_low(self,fc_bat, rc_bat):
        self.oled.display_clear()
        if fc_bat<15 and fc_bat!=-100:
            self.oled.text_fc_bat(fc_bat)
            self.oled.text_FC_battery_low()
        if rc_bat<15:
            self.oled.text_rc_bat(rc_bat)
            self.oled.text_RC_battery_low()
        self.oled.display_show()

    def get_aux(self, joysticks_data, joysticks_data_aux):
        Y_aux_max = 200
        Y_aux_min = -Y_aux_max
        R_aux_max = 200
        R_aux_min = -R_aux_max
        P_aux_max = 200
        P_aux_min = -P_aux_max
        thr, yaw, roll, pitch = joysticks_data['Thr'], joysticks_data['Yaw'], joysticks_data['Rol'], joysticks_data['Pit']
        joysticks_data_aux['Yaux'] += Absolute_to_Relative(yaw)
        joysticks_data_aux['Yaux'] = round(min(Y_aux_max, max(joysticks_data_aux['Yaux'], Y_aux_min)),1) #四舍五入，保留一位小数  #int(min(Y_aux_max, max(Y_aux, Y_aux_min)))
        joysticks_data_aux['Raux'] += Absolute_to_Relative(roll)
        joysticks_data_aux['Raux'] = round(min(R_aux_max, max(joysticks_data_aux['Raux'], R_aux_min)),1) #int(min(R_aux_max, max(R_aux, R_aux_min)))
        joysticks_data_aux['Paux'] += Absolute_to_Relative(pitch)
        joysticks_data_aux['Paux'] = round(min(P_aux_max, max(joysticks_data_aux['Paux'], P_aux_min)),1) #int(min(P_aux_max, max(P_aux, P_aux_min)))
        return joysticks_data_aux #{'Yaux':Y_aux, 'Raux':R_aux, 'Paux':P_aux} #Y_aux, R_aux, P_aux
                        
