import socket
from flask import Flask, render_template, Response, redirect
from threading import Thread
import time


### PORTS
# 5120 - initializing
# 5220 - sharing cords between pi and server
# 5320 - sharing images between pi and server
# 4123 - web server for user


def find_client():
    sock = socket.socket()
    sock.bind(('', 5120))
    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        print('connected:', addr)
        while True:
            data = conn.recv(1024)
            if data == b"legd":
                conn.send(b'lfga')
            else:
                conn.send(b'x')
            if not data:
                break
        conn.close()


def get_last_frame_from_pi():
    global last_frame, last_frame_get_time
    last_frame_tmp = b""
    sock = socket.socket()
    sock.bind(('', 5320))
    sock.listen(1)
    while True:
        try:
            conn, addr = sock.accept()
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                elif (last_frame_tmp + data)[-3:] != b"end":
                    last_frame_tmp += data
                else:
                    last_frame = (last_frame_tmp + data)[:-3]
                    last_frame_tmp = b""
                    last_frame_get_time = int(time.time())
                    # print(f"[{last_frame_get_time}] I got frame")
            conn.close()
        except:
            pass


def is_connected():
    global last_frame_get_time
    try:
        if ((int(time.time()) - last_frame_get_time) < 4):
            nw = "Connected"
        else:
            nw = "Disconnected"
        return nw
    except:
        return "Disconnected"


th_con = Thread(target=find_client)
th_con.start()
th = Thread(target=get_last_frame_from_pi)
th.start()
th_is_con = Thread(target=is_connected)
th_is_con.start()


# Web Part
# Web Part
# Web Part

app = Flask(__name__)


def gen_frames():  # generate frame by frame from camera
    global last_frame
    with open("sth_wrong.jpg", "rb") as f:
        sth_wrong = f.read()
    while True:
        try:
            if is_connected() == "Disconnected":
                frame = sth_wrong
            else:
                frame = last_frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
        except:
            pass

# для человечков
@app.route("/")
def index():
    return render_template("index.html", iscon=is_connected())


@app.route("/fst_boot")
def first_stp():
    return render_template("first_setting.html", iscon=is_connected())


@app.route("/fst_boot/ai")
def first_ai():
    return render_template("first_ai.html", iscon=is_connected())


@app.route("/fst_boot/auto")
def first_auto():
    return render_template("first_auto.html", iscon=is_connected())


@app.route("/fst_boot/manual")
def first_manual():
    return render_template("first_manual.html", iscon=is_connected())


@app.route("/sett")
def setts():
    return render_template("settings.html")


@app.route("/m_s")
def manual_shooting():
    return render_template("manualsh.html")


@app.route("/about")
def kto():
    return render_template("about_us.html")


# вспомогательные
@app.route("/shooter/<w>/<h>/<w_max>/<h_max>")
def shooter(w, h, w_max, h_max):
    print(str(w) + "/" + str(w_max) + " " + str(h) + "/" + str(h_max))
    return "ok"


@app.route("/shoot")
def shoot():
    return "ok"


@app.route("/video")
def video():
    while True:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


app.run(host="0.0.0.0", debug=False, port=4123) ### Если вклчить отладку, то она начнёт конфликтовать с многопоточностью, и в результате мы получим нерабочую/забаганную прогу
