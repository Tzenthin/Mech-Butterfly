from Kang_RC import RC

#60:55:f9:bc:c2:20
#peer_mac = b'\x60\x55\xf9\xbc\xc2\x20'
#peer_mac = b'\xf0\xf5\xbd\xfb\x19\xc0'
#6055f9c9b38c
#peer_mac = b'\x60\x55\xf9\xc9\xb3\x8c'
#6055f9c9c1dc
#peer_mac = b'\x60\x55\xf9\xc9\xc1\xdc'
#f0f5bdfb0e14
peer_mac = b'\xf0\xf5\xbd\xfb\x2d\xa4'
#f0:f5:bd:fb:0e:dc
peer_mac = b'\xf0\xf5\xbd\xfb\x0e\xdc'

#60:55:f9:2b:30:a0
peer_mac = b'\x60\x55\xf9\x2b\x30\xa0'
#6055f9bde030
peer_mac = b'\x60\x55\xf9\xbd\xe0\x30'
#50:78:7d:92:74:80
peer_mac = b'\x50\x78\x7d\x92\x74\x80'
remot_control = RC()
remot_control.add_peer(peer_mac)
remot_control.run()
