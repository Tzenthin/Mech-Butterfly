import network
import espnow
import time
#from Kang_Mac import format_mac_addr, mac_address_to_bytes
import json

class Esp_Comm():
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
        #self.fc_height = -100
        #self.fc_temp = -100
        self.fc_data = {'fc_bat':-100, 'fc_height':-100, 'fc_temp':-100}
        self.e.irq(self._recv_callback)
        self.succ_flag = 0
    def _recv_callback(self, tmp):
        #while True:  # Read out all messages waiting in the buffer
        #global flyer_bat
        mac, msg = self.e.irecv(0)  # 0ms means Don't wait if no messages left
        if mac is None:
            return
        msg = msg.decode()
        self.fc_data =  json.loads(msg)
        '''
        self.fc_bat = msg['fc_bat']
        self.fc_height = msg['fc_height']
        self.fc_temp = msg['fc_temp']
        '''
        #print(mac, msg)
    def send(self, joysticks_data, joysticks_data_aux, key_command): #Dict
        #joysticks_data = ' '.join([str(e) for e in joysticks_data])
        joysticks_data.update(joysticks_data_aux)
        joysticks_data.update(key_command)
        #send_data = {"Thr":pre_joysticks_data_list[0], "Yaw":pre_joysticks_data_list[1], "Rol":pre_joysticks_data_list[2], "Pit":pre_joysticks_data_list[3],\
        #            "Yaux":Y_aux, "Raux":R_aux, "Paux":P_aux, "Lock":lock, "Fix":fix_height,"Imu":imu }
        send_data = json.dumps(joysticks_data)
        print(send_data)
        self.succ_flag = self.e.send(self.peer, send_data, True)
 
 
if __name__ == "__main__":
    peer = b'\xec\xda\x3b\xd1\x68\x30'
    esp_now = Esp_Comm(peer)
    for i in range(0, 100):
        esp_now.send(str(i))
        time.sleep(0.1)