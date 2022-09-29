import socket
from flask import Flask, render_template, Response, redirect
import requests
from base64 import decode
import cv2
from threading import Thread
from time import sleep


def find_client():
    sock = socket.socket()
    sock.bind(('', 5120))
    sock.listen(1)
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
    cap = cv2.VideoCapture('test.mp4')
    i = 0
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        last_frame = cv2.imencode('.jpg', frame)[1].tobytes()
        i += 1



# find_client()
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
    return redirect("/")

@app.route("/shoot")
def shoot():
    return "ok"

@app.route("/video")
def video():
    while True:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

app.run(host="0.0.0.0", debug=True, port=4123)