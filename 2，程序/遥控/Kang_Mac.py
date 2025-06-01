import ubinascii
import network


def Get_Mac_ID():
    wlan_sta = network.WLAN(network.STA_IF)
    wlan_sta.active(True)
    wlan_mac = wlan_sta.config('mac')
    mac_id = ubinascii.hexlify(wlan_mac).decode()
    #print(mac_id)
    mac_id = format_mac_addr(mac_id)
    return mac_id


def format_mac_addr(addr):
    mac_addr = addr
    mac_addr = mac_addr.lower() #upper()
    new_mac = ""
    for i in range(0, len(mac_addr),2):
        #print(mac_addr[i] + mac_addr[i+1])
        if (i == len(mac_addr) - 2):
            new_mac = new_mac + mac_addr[i] + mac_addr[i+1]
        else:
            new_mac = new_mac + mac_addr[i] + mac_addr[i+1] + ":"
    #print("----------------------------------------")
    #print("My MAC Address:" + new_mac)
    #print("----------------------------------------")
    return new_mac

def mac_address_to_bytes(mac_address):
    # 假设MAC地址格式为'AA:BB:CC:DD:EE:FF'
    # 使用':'分割字符串，然后转换每个部分为整数，并转换为字节
    bytes_mac = bytes([int(part, 16) for part in mac_address.split(':')])
    return bytes_mac

def mac_address_to_bytes(mac_address):
    # 假设MAC地址格式为'AA:BB:CC:DD:EE:FF'
    # 使用':'分割字符串，然后转换每个部分为整数，并转换为字节
    bytes_mac = bytes([int(part, 16) for part in mac_address.split(':')])
    return bytes_mac

if __name__ == "__main__":
    mac = Get_Mac_ID()
    print(mac)
    #mac = mac_address_to_bytes(mac)
    #print(type(mac), mac)
    #print(mac_address_to_bytes("1A:2B:3C:4D:5E:6F"))

#  543204782e60
