from flask import Flask, render_template, Response, redirect, request, make_response
from werkzeug.utils import secure_filename
import cv2
from threading import Thread
import socket
import time
import os


### PORTS
# 5120 - initializing
# 5220 - sharing cords between pi and server
# 5121 - sharing stats between pi and server
# 5320 - sharing images between pi and server
# 4123 - web server for user


def find_client():
    global connected_ip
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
                connected_ip = addr[0]
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


def get_stats_from_pi():
    global stats_conf
    sock = socket.socket()
    sock.bind(('', 5121))
    sock.listen(1)
    while True:
        try:
            conn, addr = sock.accept()
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                elif data[0] == "s":
                    stats_conf = data.split("_")
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


def send_cords_to_pi(cords):
    global connected_ip
    try:
        sock = socket.socket()
        sock.connect((connected_ip, 5220))
        sock.send(cords.encode())
        sock.close()
    except Exception as ex:
        print(ex)


th_con = Thread(target=find_client)
th_con.start()
th_stats = Thread(target=get_stats_from_pi)
th_stats.start()
th = Thread(target=get_last_frame_from_pi)
th.start()


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


@app.route("/send_file", methods=['POST'])
def send_file():
    print("tipa prinyal")

# для человечков

@app.errorhandler(404)
def error_404(e):
    return render_template("err404.html")


@app.route("/")
def index():
    if need_setup:
        return redirect("/fst_boot")
    else:
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


@app.route("/swmode/auto")
def swm_auto():
    print("new mode is auto")
    return redirect("/sett")

@app.route("/swmode/ai")
def swm_ai():
    print("new mode is ai")
    return redirect("/sett")

@app.route("/swmode/manual")
def swm_manual():
    print("new mode is manual")
    return redirect("/sett")


@app.route("/sett")
def setts():
    global stats_conf
    try:
        print(stats_conf)
        st_cpu_temp = int(stats_conf[1])
        st_used_ram = float(stats_conf[2])
        st_total_ram = float(stats_conf[3])
        st_used_mem = float(stats_conf[4])
        st_total_mem = float(stats_conf[5])
    except:
        st_cpu_temp = 52
        st_used_ram = 0.56
        st_total_ram = 0.94
        st_used_mem = 9.6
        st_total_mem = 14.4
    st_actually = (is_connected() == "Connected")
    if not request.cookies.get('language') or request.cookies.get('language') == "en":
        if st_cpu_temp > 85:
            if st_actually:
                return render_template("settings_en.html", used_ram=st_used_ram, total_ram=st_total_ram, used_mem=st_used_mem,
                                        total_mem=st_total_mem, cpu_temp=85, cpu_d_temp=st_cpu_temp,
                                        temp_c="rgb(240, 100, 100)",
                                        is_act="")
            else:
                return render_template("settings_en.html", used_ram=st_used_ram, total_ram=st_total_ram, used_mem=st_used_mem,
                                       total_mem=st_total_mem, cpu_temp=85, cpu_d_temp=st_cpu_temp,
                                       temp_c="rgb(240, 100, 100)",
                                       is_act="outdated")
        else:
            if st_actually:
                return render_template("settings_en.html", used_ram=st_used_ram, total_ram=st_total_ram, used_mem=st_used_mem,
                                       total_mem=st_total_mem, cpu_temp=st_cpu_temp, cpu_d_temp=st_cpu_temp, temp_c="white",
                                       is_act="")
            else:
                return render_template("settings_en.html", used_ram=st_used_ram, total_ram=st_total_ram, used_mem=st_used_mem,
                                       total_mem=st_total_mem, cpu_temp=st_cpu_temp, cpu_d_temp=st_cpu_temp, temp_c="white",
                                       is_act="outdated")
    else:
        if st_cpu_temp > 85:
            if st_actually:
                return render_template("settings_ru.html", used_ram=st_used_ram, total_ram=st_total_ram, used_mem=st_used_mem,
                                        total_mem=st_total_mem, cpu_temp=85, cpu_d_temp=st_cpu_temp,
                                        temp_c="rgb(240, 100, 100)",
                                        is_act="")
            else:
                return render_template("settings_ru.html", used_ram=st_used_ram, total_ram=st_total_ram, used_mem=st_used_mem,
                                       total_mem=st_total_mem, cpu_temp=85, cpu_d_temp=st_cpu_temp,
                                       temp_c="rgb(240, 100, 100)",
                                       is_act="outdated")
        else:
            if st_actually:
                return render_template("settings_ru.html", used_ram=st_used_ram, total_ram=st_total_ram, used_mem=st_used_mem,
                                       total_mem=st_total_mem, cpu_temp=st_cpu_temp, cpu_d_temp=st_cpu_temp, temp_c="white",
                                       is_act="")
            else:
                return render_template("settings_ru.html", used_ram=st_used_ram, total_ram=st_total_ram, used_mem=st_used_mem,
                                       total_mem=st_total_mem, cpu_temp=st_cpu_temp, cpu_d_temp=st_cpu_temp, temp_c="white",
                                       is_act="outdated")


def kostil_kirila():
    return redirect("/sett")


@app.route("/sett/ru")
def set_ru_lng():
    res = make_response(kostil_kirila())
    res.set_cookie('language', 'ru', max_age=315360000)
    return res


@app.route("/sett/en")
def set_en_lng():
    res = make_response(kostil_kirila())
    res.set_cookie('language', 'en', max_age=315360000)
    return res


@app.route("/sett/br_ru")
def set_br_ru_lng():
    res = make_response(kostil_kirila())
    res.set_cookie('language', 'br_ru', max_age=315360000)
    return res


@app.route("/sett/br_en")
def set_br_en_lng():
    res = make_response(kostil_kirila())
    res.set_cookie('language', 'br_en', max_age=315360000)
    return res


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
    send_cords_to_pi("c_" + str(w) + "_" + str(w_max) + "_" + str(h) + "_" + str(h_max))
    return "ok"


@app.route('/get_model', methods=['POST'])
def uploadd_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save("model.hzkakoiformat")
        return 'file uploaded successfully'


@app.route("/shoot")
def shoot():
    return "ok"


@app.route("/video")
def video():
    while True:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if os.path.exists("cfg.txt"):
    with open("cfg.txt") as f:
        cfg = f.read()
        c_mode = cfg[0]
        need_setup = False
else:
    need_setup = False ### В самом конце замени на True

app.run(host="0.0.0.0", debug=False, port=4123) ### Если вклчить отладку, то она начнёт конфликтовать с многопоточностью, и в результате мы получим нерабочую/забаганную прогу
