import os
import platform
import threading
import socket
from datetime import datetime


def scan_Ip(ip):
    global local_ips
    addr = net + str(ip)
    comm = ping_com + addr
    response = os.popen(comm)
    data = response.readlines()
    for line in data:
        if 'TTL' in line:
            local_ips.append(addr)
            break


def is_it_host():
    global local_ips
    for s_ip in local_ips:
        try:
            sock = socket.socket()
            sock.connect((s_ip, 5120))
            sock.send(b'legd')
            data = sock.recv(1024)
            sock.close()
            if data == b'lfga':
                return s_ip
        except:
            pass


local_ips = []
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Создаем сокет (UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Настраиваем сокет на BROADCAST вещание.
s.connect(('<broadcast>', 0))
net = s.getsockname()[0]
print('Your IP :', net)
net_split = net.split('.')
a = '.'
net = net_split[0] + a + net_split[1] + a + net_split[2] + a
oc = platform.system()
if (oc == "Windows"):
    ping_com = "ping -n 1 "
else:
    ping_com = "ping -c 1 "
t1 = datetime.now()
print("Scanning in Progress")
for ip in range(0, 80):
    if ip == int(net_split[3]):
       continue
    potoc = threading.Thread(target=scan_Ip, args=[ip])
    potoc.start()
potoc.join()
t2 = datetime.now()
total = t2 - t1

print("Scanning completed in: ", total)
print(local_ips)
host = is_it_host()
print(host)