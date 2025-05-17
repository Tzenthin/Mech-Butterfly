from Kang_Flyer_Ornithopter import Ornithopter


peer_mac = b'\x54\x32\x04\x73\xc2\x40'
#54:32:04:78:31:40
peer_mac = b'\x54\x32\x04\x78\x31\x40'

plane = Ornithopter()
#plane.set_pid(1.0, 0.01, 0.01, 1.8, 0.01, 0.01, 2, 0, 0, 50)
plane.add_peer(peer_mac)
#plane.start()
plane.fly_loop()
