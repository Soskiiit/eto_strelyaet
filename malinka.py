import os
import platform
import threading
import socket
from datetime import datetime
import cv2


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
    # изменить потом не забудь а то пиздец кринге будет
    # изменить потом не забудь а то пиздец кринге будет
    # изменить потом не забудь а то пиздец кринге будет
    cap = cv2.VideoCapture('test.mp4')
    i = 0
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        last_frame = cv2.imencode('.jpg', frame)[1].tobytes()
        i += 1
        send_photos(last_frame)


def send_photos(last_frame):
    # изменить потом не забудь а то пиздец кринге будет
    # изменить потом не забудь а то пиздец кринге будет
    # изменить потом не забудь а то пиздец кринге будет
    pass


host = None
while host == None:
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
        potoc = threading.Thread(target=scan_Ip, args=[ip])
        potoc.start()
    potoc.join()
    t2 = datetime.now()
    total = t2 - t1
    print("Scanning completed in: ", total)
    print(local_ips)
    host = is_it_host()
    print(host)
make_photos()