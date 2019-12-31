import socket
import qrcode

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
ip = s.getsockname()[0]
s.close()

img = qrcode.make('http://'+ip+':6500')
img.save('web_address.png')
