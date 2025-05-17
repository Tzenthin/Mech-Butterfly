import network
import espnow
import time
#from Kang_Mac import format_mac_addr, mac_address_to_bytes
import json

class Esp_Comm_FC():
    def __init__(self, peer=b'\xec\xda\x3b\xd1\x68\x30'):
        # A WLAN interface must be active to send()/recv()
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        sta.disconnect()   # Because ESP8266 auto-connects to last Access Point
        self.e = espnow.ESPNow()
        self.e.active(True)
        #b'\xec\xda\x3b\xaa\xe4\x88'   # MAC address of peer's wifi interface
        self.peer = peer
        self.e.add_peer(peer)      # Must add_peer() before send()
        #self.fc_bat=-100
        #self.flight_height = -100
        self.e.irq(self._recv_callback)
        self.succ_flag=0
        self.send_fail_time = 0
        
        # 10个通道数据
        self.rc_thr = 0
        self.rc_yaw = 500
        self.rc_rol = 500
        self.rc_pit = 500
        self.rc_yaw_aux = 0
        self.rc_rol_aux = 0
        self.rc_pit_aux = 0
        self.rc_lock = 1
        self.rc_fix = 0
        self.rc_imu = 0
        
    def _recv_callback(self, tmp):
        #while True:  # Read out all messages waiting in the buffer
        #global flyer_bat
        mac, msg = self.e.irecv(0)  # 0ms means Don't wait if no messages left
        if mac is None:
            return
        msg = msg.decode()
        msg = json.loads(msg)
        #print(msg)
        self.rc_thr = msg["Thr"]#eval(msg["Thr"])
        self.rc_yaw = msg["Yaw"]#eval(msg["Yaw"])
        self.rc_rol = msg["Rol"]#eval(msg["Rol"])
        self.rc_pit = msg["Pit"]#eval(msg["Pit"])
        self.rc_yaw_aux = msg['Yaux']#eval(msg['Y_aux'])
        self.rc_rol_aux = msg["Raux"]#eval(msg["R_aux"])
        self.rc_pit_aux = msg["Paux"]#eval(msg["P_aux"])
        self.rc_fix = msg["Fix"]#eval(msg["Fix"])
        self.rc_imu = msg["Imu"]#eval(msg["Imu"])
        self.rc_lock = msg["Lock"]#eval(msg["Lock"])
        #if self.send_fail_time>5:
        #    self.rc_lock=1
            
        #self.rc_thr = msg.decode().split()[0]
        #self.flight_height = msg.decode().split()[1]
        #print(mac, msg)
    def send(self, msg_str):
        self.succ_flag = self.e.send(self.peer, msg_str, True)
        if self.succ_flag==False:
            self.send_fail_time += 1
        else:
            self.send_fail_time=0
        #飞控像遥控发送电池高度等数据，如果发送失败，意味着通信中断，则将飞控上锁
        if self.send_fail_time>3:
            self.rc_lock = 1
        #print(self.send_fail_time)
 
 
if __name__ == "__main__":
    peer = b'\xec\xda\x3b\xd1\x68\x30'
    esp_now = Esp_Comm(peer)
    for i in range(0, 100):
        esp_now.send(str(i))
        time.sleep(0.1)