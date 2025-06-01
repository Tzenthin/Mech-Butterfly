import time
from Kang_Joystick import  Absolute_to_Relative

def wait_for_mode_select(oled, Key_X):
    while True:
            oled.display_clear()
            if Key_X.double_click: #如果双击，便退出模式选择界面，此时在class中，mode的值也已经确定了
                break
            if Key_X.selection:  #1
                oled.text_menu_select_control()
            else:
                oled.text_menu_select_charge()
            oled.display_show()
            #因为双击时间设定为500ms内。所以，为了不在第一次击的时候就显示切换到下一个选项，这里的延时要大于500ms，才能看起来符合人的习惯
            time.sleep_ms(2000)


def charging(bat, oled, beep):
    i=0
    while True:
        bat_data = bat.battery_read_remaining()[1]
        time.sleep(0.01)
        if i%20==0:
            oled.display_clear()
            oled.text_rc_bat(bat_data)
            oled.display_show()
        i+=1
        if bat_data>96:
            beep.didi()
            #
        #time.sleep(1)
    
def oled_display_battery_low(oled, fc_bat, rc_bat):
    oled.display_clear()
    if fc_bat<15 and fc_bat!=-100:
        oled.text_fc_bat(fc_bat)
        oled.text_FC_battery_low()
    if rc_bat<15:
        oled.text_rc_bat(rc_bat)
        oled.text_RC_battery_low()
    oled.display_show()
    
def get_aux(joysticks_data, joysticks_data_aux):
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
                    
                    
                    