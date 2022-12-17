import os
import platform
from threading import Thread
import socket
from datetime import datetime
import cv2
import time
import psutil


### PORTS
# 5120 - initializing
# 5220 - sharing cords between pi and server
# 5121 - sharing stats between pi and server
# 5320 - sharing images between pi and server
# 4123 - web server for user


def scan_Ip(ip):
    global local_ips
    addr = net + str(ip)
    comm = ping_com + addr
    response = os.popen(comm)
    data = response.readlines()
    for line in data:
        if 'TTL' in line or "ttl" in line:
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


def aim_n_shoot(x, y):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 5220))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(data)


def make_photos():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        last_frame = cv2.imencode('.jpg', frame)[1].tobytes()
        try:
            send_photos(last_frame)
        except:
            pass


def send_photos(last_frame):
    global host_ip
    sock = socket.socket()
    sock.connect((host_ip, 5320))
    sock.send(last_frame)
    sock.send(b"end")
    sock.close()
    # print(f"[{time.time()}] I sent frame")

def send_stats():
    while True:
        s_disk_total = round((psutil.disk_usage("/").total / 1073741824), 1) # get statistics and convert it to gb
        s_disk_used = round((psutil.disk_usage("/").used / 1073741824), 1) # get statistics and convert it to gb
        s_ram_total = round((psutil.virtual_memory().total / 1073741824), 1) # get statistics and convert it to gb
        s_ram_used = round((psutil.virtual_memory().used / 1073741824), 1) # get statistics and convert it to gb
        try:
            s_cpu_temp = int(psutil.sensors_temperatures()["cpu_thermal"][0].current)
            # need for tests because psutil.sensors_... works only on linux
        except:
            s_cpu_temp = 50
        try:
            sock = socket.socket()
            sock.connect((host_ip, 5121))
            stats = "s_" + str(s_cpu_temp) + "_" + str(s_ram_used) + "_" + str(s_ram_total) + "_" + str(s_disk_used) + "_" + str(s_disk_total)
            stats_bytes = stats.encode(encoding = 'UTF-8')
            sock.send(stats_bytes)
            sock.close()
        except Exception as ex:
            print(ex)
        time.sleep(1)


def get_cords():
    global cords
    sock = socket.socket()
    sock.bind(('', 5220))
    sock.listen(1)
    while True:
        try:
            conn, addr = sock.accept()
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                elif data[0] == "c":
                    cords = [int(data.split("_")[1]) / int(data.split("_")[2]), int(data.split("_")[3]) / int(data.split("_")[4])]
            conn.close()
            print(cords)
        except:
            pass


host_ip = None
while host_ip == None:
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
    for ip in range(0, 181):
        potoc = Thread(target=scan_Ip, args=[ip])
        potoc.start()
    potoc.join()
    t2 = datetime.now()
    total = t2 - t1
    print("Scanning completed in: ", total)
    print(local_ips)
    host_ip = is_it_host()
    if host_ip != None:
        print("host ip: " + host_ip)
    else:
        print("retrying to search host")


th = Thread(target=send_stats)
th.start()
th_capture = Thread(target=make_photos)
th_capture.start()
th_cords = Thread(target=get_cords)
th_cords.start()
