import math
import time

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def wrap_180(x):
  return x+360 if x < -180 else (x-360 if x > 180 else x)


def bmp280_altitude_calibration(bmp):
    alt_sum = 0
    cal_cnt = 10
    for i in range(cal_cnt):
        #pressure=bmp.pressure
        #p_bar=pressure/100000
        #p_mmHg=pressure/133.3224
        #temperature=bmp.temperature
        #print("Temperature: {} C".format(temperature))
        #print("Pressure: {} Pa, {} bar, {} mmHg".format(pressure,p_bar,p_mmHg))
        alt = bmp.read_altitude()
        alt_sum += alt
        #print(alt)
        time.sleep(0.1)
    altitude = alt_sum/cal_cnt
    return altitude
'''
def bmp280_read_altitude(bmp):
    pressure=bmp.pressure
    alt = bmp.read_altitude(pressure)
    return alt
'''

def mpu6050_calibration(mpu, packetSize, cali_cnt):
    pitch_tmp = 0
    roll_tmp = 0
    yaw_tmp = 0
    for i in range(cali_cnt):
        mpuIntStatus = mpu.getIntStatus()
        fifoCount = mpu.getFIFOCount()
        if mpuIntStatus < 2 or fifoCount == 1024:
            mpu.resetFIFO()
            #print('FIFO overflow!')
            continue
        while fifoCount < packetSize:
            fifoCount = mpu.getFIFOCount()
        #fifoCount -= packetSize
        fifoBuffer = mpu.getFIFOBytes(packetSize)
        '''
        quat = mpu.DMP_get_quaternion_int16(FIFO_buffer)
        yaw, rol, pit = mpu.dmpGetEuler(*mpu.dmpGetQuaternion(fifoBuffer))
        g_pit, g_rol, g_yaw = mpu.dmpGetGyro(fifoBuffer)
        '''
        #accel = mpu.DMP_get_acceleration_int16(FIFO_buffer)
        quat = mpu.dmpGetQuaternion(fifoBuffer)
        grav = mpu.dmpGetGravity(quat)
        roll_pitch_yaw = mpu.dmpGetYawPitchRoll(quat, grav)
        roll = roll_pitch_yaw['roll']* (180.0 / math.pi)
        pitch = roll_pitch_yaw['pitch']* (180.0 / math.pi)
        yaw = roll_pitch_yaw['yaw']* (180.0 / math.pi) 
        roll_tmp +=  roll
        pitch_tmp += pitch
        yaw_tmp += yaw
    roll_offset = roll_tmp/cali_cnt
    pitch_offset = pitch_tmp/cali_cnt
    yaw_offset = yaw_tmp/cali_cnt
    return roll_offset, pitch_offset, yaw_offset


def mpu6050_read_data(mpu, packetSize):
    mpuIntStatus = mpu.getIntStatus()
    fifoCount = mpu.getFIFOCount()
    if mpuIntStatus < 2 or fifoCount == 1024:
        mpu.resetFIFO()
        #print('FIFO overflow!')
        #continue
        return None
    while fifoCount < packetSize:
        fifoCount = mpu.getFIFOCount()
    #fifoCount -= packetSize
    fifoBuffer = mpu.getFIFOBytes(packetSize)

    quat = mpu.dmpGetQuaternion(fifoBuffer)
    grav = mpu.dmpGetGravity(quat)
    roll_pitch_yaw = mpu.dmpGetYawPitchRoll(quat, grav)
    gyro_roll_pitch_yaw = mpu.dmpGetGyro(fifoBuffer)
    roll = roll_pitch_yaw['roll']* (180.0 / math.pi)
    pitch = roll_pitch_yaw['pitch']* (180.0 / math.pi)
    yaw = roll_pitch_yaw['yaw']* (180.0 / math.pi)
    gyro_roll = gyro_roll_pitch_yaw[0]
    #根据对数据的观察，pitch 坐标系的关系，此处需要加上一个负号，才能保证角度和角速度的方向相同
    gyro_pitch = - gyro_roll_pitch_yaw[1]
    #根据对数据的观察，yaw 坐标系的关系，此处需要加上一个负号，才能保证角度和角速度的方向相同
    gyro_yaw = - gyro_roll_pitch_yaw[2]
    
    return (roll, pitch, yaw, gyro_roll, gyro_pitch, gyro_yaw)

def calculate_motor_speed(rc_thr_width, rc_rol_width, rc_pit_width, rc_yaw_width,
                          ra_pid, pa_pid, ya_pid,
                          rr_pid, pr_pid, yr_pid,
                          roll, pitch,yaw,
                          gyro_roll, gyro_pitch, gyro_yaw,
                          roll_offset, pitch_offset, yaw_offset):
    # Angle PIDS，角度环，外环PID
    rol_angle_out = max(min(ra_pid.get_pid(rc_rol_width - (roll -roll_offset), 1), 250), -250)
    pit_angle_out = max(min(pa_pid.get_pid(rc_pit_width - (pitch-pitch_offset), 1), 250), -250)
    #yaw轴的数据漂移比较大，平均1秒漂移1度
    yaw_angle_out = max(min(ya_pid.get_pid(wrap_180(rc_yaw_width+(yaw -yaw_offset)), 1), 360), -360)
    #yaw_stab_out = max(min(ys_pid.get_pid(wrap_180(yaw-yaw_offset), 1), 360), -360)
    #if abs(rc_yaw_width) > 10:
    #    yaw_stab_out = rc_yaw_width
    #    yaw_target = roll_pitch_yaw['yaw']
    # rate PIDS，角速度环，内环PID
    rol_out = max(min(rr_pid.get_pid(rol_angle_out - gyro_roll, 1), 500), -500)
    pit_out = max(min(pr_pid.get_pid(pit_angle_out - gyro_pitch, 1), 500), -500)
    yaw_out = max(min(yr_pid.get_pid(yaw_angle_out - gyro_yaw, 1), 500), -500)

    m1_speed = rc_thr_width + pit_out - rol_out# + yaw_out #rc_thr_width + pit_out + rol_out - yaw_out
    m2_speed = rc_thr_width + pit_out + rol_out# - yaw_out #rc_thr_width + pit_out - rol_out + yaw_out 
    m3_speed = rc_thr_width - pit_out + rol_out# + yaw_out    #rc_thr_width - pit_out + rol_out + yaw_out 
    m4_speed = rc_thr_width - pit_out - rol_out# - yaw_out  #rc_thr_width - pit_out - rol_out - yaw_out
    
    return m1_speed, m2_speed, m3_speed, m4_speed


def Calculate_Angle_PID(rc_rol_width, rc_pit_width, rc_yaw_width,
                        ra_pid, pa_pid, ya_pid,
                        roll, pitch,yaw,
                        roll_offset, pitch_offset, yaw_offset
                        ):
    # Angle PIDS，角度环，外环PID
    rol_angle_out = max(min(ra_pid.get_pid(-rc_rol_width - (roll -roll_offset), 1), 250), -250)
    pit_angle_out = max(min(pa_pid.get_pid(rc_pit_width - (pitch-pitch_offset), 1), 250), -250)
    #yaw轴的数据漂移比较大，平均1秒漂移1度
    yaw_angle_out = max(min(ya_pid.get_pid(wrap_180(rc_yaw_width-(yaw -yaw_offset)), 1), 360), -360)
    return rol_angle_out, pit_angle_out, yaw_angle_out

def Calculate_Rate_PID(rc_thr_width,
                       rr_pid, pr_pid, yr_pid,
                       rol_angle_out, pit_angle_out, yaw_angle_out,
                       gyro_roll, gyro_pitch, gyro_yaw
                       ):
    # rate PIDS，角速度环，内环PID
    rol_out = max(min(rr_pid.get_pid(rol_angle_out - gyro_roll, 1), 500), -500)
    pit_out = max(min(pr_pid.get_pid(pit_angle_out - gyro_pitch, 1), 500), -500)
    yaw_out = max(min(yr_pid.get_pid(yaw_angle_out - gyro_yaw, 1), 500), -500)
    '''
    m1_speed = rc_thr_width + pit_out - rol_out# + yaw_out #rc_thr_width + pit_out + rol_out - yaw_out
    m2_speed = rc_thr_width + pit_out + rol_out# - yaw_out #rc_thr_width + pit_out - rol_out + yaw_out 
    m3_speed = rc_thr_width - pit_out + rol_out# + yaw_out    #rc_thr_width - pit_out + rol_out + yaw_out 
    m4_speed = rc_thr_width - pit_out - rol_out# - yaw_out  #rc_thr_width - pit_out - rol_out - yaw_out
    '''
    m1_speed = rc_thr_width + pit_out - rol_out + yaw_out #rc_thr_width + pit_out + rol_out - yaw_out
    m2_speed = rc_thr_width - pit_out - rol_out - yaw_out #rc_thr_width + pit_out - rol_out + yaw_out 
    m3_speed = rc_thr_width - pit_out + rol_out + yaw_out    #rc_thr_width - pit_out + rol_out + yaw_out 
    m4_speed = rc_thr_width + pit_out + rol_out - yaw_out  #rc_thr_width - pit_out - rol_out - yaw_out
    
    return m1_speed, m2_speed, m3_speed, m4_speed

def Calculate_PID_M2S2(rc_thr_width,
                        roll_target, pitch_target, yaw_target,
                        ra_pid, pa_pid, ya_pid,
                        roll, pitch,yaw,
                        roll_offset, pitch_offset, yaw_offset
                        ):#固定翼的两个电机，两个舵机
    roll = roll - roll_offset
    pitch = pitch - pitch_offset
    roll, pitch = -pitch, roll
    
    # rate PIDS，角速度环，内环PID
    #roll, pitch = -roll, -pitch  #-pitch, -roll
    rol_out = max(min(ra_pid.get_pid(roll_target - roll, 1), 60), -60)
    pit_out = max(min(pa_pid.get_pid(pitch_target - pitch, 1), 60), -60)
    #pit_out = pit_out * abs(math.sin(roll))   # 用roll姿态补偿升降舵
    
    '''
    #如果遥控器给的roll大于阈值，表明yaw的作用为辅助完成横滚动作的，否则yaw用来保持飞机的航向稳定
    if abs(roll_target)>1:
        #可以根据roll的控制量配合计算相应的速度值
        yaw_out=0
        #m_left = rc_thr_width
        #m_right = rc_thr_width
        #或者，两个电机的速度保持一致
        
        #yaw_out = rol_out * 10  # 
        #m_left = rc_thr_width + yaw_out
        #m_right = rc_thr_width - yaw_out
        
    else:
        yaw_out = max(min(ya_pid.get_pid(yaw_target - yaw + yaw_offset, 1), 100), -100)
        #m_left = rc_thr_width - yaw_out
        #m_right = rc_thr_width + yaw_out
    '''
    return rol_out, pit_out#, yaw_out #m_left, m_right, 
    

def Calculate_PID_pitch_yaw(rc_thr_width,
                        pitch_target, yaw_target,
                        pa_pid, ya_pid,
                        roll, pitch,yaw,
                        roll_offset, pitch_offset, yaw_offset
                        ):#固定翼的两个电机，两个舵机
    #这里很关键，因为安装方式的原因，需要根据实际情况来重新判断旋转轴
    #此外还要注意方向的问题
    pitch, yaw = roll, pitch
    pitch_offset, yaw_offset = roll_offset, pitch_offset
    pit_out = max(min(pa_pid.get_pid(pitch_target - pitch + pitch_offset, 1), 30), -30)
    #pit_out = pit_out * abs(math.sin(roll))   # 用roll姿态补偿升降舵
    yaw_out = max(min(ya_pid.get_pid(yaw_target - yaw + yaw_offset, 1), 30), -30)
    
    return pit_out, yaw_out

def Calculate_PID_roll_pitch(rc_thr_width,
                            roll_target, pitch_target, 
                            ra_pid,pa_pid,
                            roll, pitch,
                            roll_offset, pitch_offset
                            ):
    roll = roll - roll_offset
    pitch = pitch - pitch_offset
    roll, pitch = pitch, -roll
    
    roll_out = max(min(ra_pid.get_pid(roll_target - roll , 1), 60), -60)
    pit_out = max(min(pa_pid.get_pid(pitch_target - pitch, 1), 60), -60)
    #pit_out = pit_out * abs(math.sin(roll))   # 用roll姿态补偿升降舵
    pitch_left = pit_out - roll_out
    pitch_right = -pit_out - roll_out
    return pitch_left, pitch_right


