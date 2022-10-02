import socket
from flask import Flask, render_template, Response, redirect
import requests
from base64 import decode
import cv2
from threading import Thread
from time import sleep


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
    global last_frame
    pass



th_con = Thread(target=find_client)
th_con.start()
th = Thread(target=get_last_frame_from_pi)
th.start()

# Web Part
# Web Part
# Web Part

app = Flask(__name__)


def gen_frames():  # generate frame by frame from camera
    global last_frame
    while True:
        frame = last_frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route("/")
def index():
    return render_template("index_js.html")

@app.route("/shooter/<w>/<h>")
def shooter(w, h):
    print(w, h)
    return "ok"

@app.route("/shoot")
def shoot():
    return "ok"

@app.route("/video")
def video():
    while True:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



app.run(host="0.0.0.0", debug=True, port=4123)