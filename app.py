import socket
import qrcode
import threading
import os
from yt_dlp import YoutubeDL
from flask import Flask, render_template, request, redirect, flash
from flask_httpauth import HTTPDigestAuth
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

app = Flask(__name__)
app.secret_key = os.urandom(12).hex()
auth = HTTPDigestAuth()

download_lock = threading.Lock()

users = {
    "bryce": "bryce"
}

queue = []

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

# Mobile Routes
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['player_control'] == 'restart':
            v = driver.execute_script("""const video = document.getElementById('video');
                        video.currentTime = 0;""")
            return redirect('/')
        elif request.form['player_control'] == 'pause':
            v = driver.execute_script("""const video = document.getElementById('video');
                                    if (!video.paused) {
                                        video.pause();
                                    } else {
                                        video.play();
                                    }""")
            return redirect('/')
        elif request.form['player_control'] == 'skip':
            v = driver.execute_script("""const video = document.getElementById('video');
                        video.currentTime = video.duration;""")
            return redirect('/')
    elif request.method == 'GET':
        return render_template("mobile_index.html", active="home")

@app.route("/queue")
def queue():
    return render_template("queue.html", active="queue")

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        song = request.form['song']
        download_thread = threading.Thread(target=download_video, args=(song,))
        download_thread.start()
        flash("Song added to queue")
        return redirect('/')
    elif request.method == 'GET':
        return render_template("search.html", active="search")

@app.route("/admin")
@auth.login_required
def admin():
    return render_template("admin.html", active="admin")

# TV Routes
@app.route("/tv")
def tv():
    # get local ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.0.0.0", 0))

    local_ip = s.getsockname()[0]
    qr = qrcode.make(local_ip)
    qr.save("./qrcode.png")

    return render_template("tv_index.html", local_ip=local_ip)

@app.route('/play_video')
def play_video():
    return render_template("video_player.html")

def run_selenium():
    global driver
    firefox_options = Options()
    firefox_options.set_preference("media.autoplay.default", 0)
    driver = webdriver.Firefox(options=firefox_options)

    driver.get('http://127.0.0.1:8080/tv')
    driver.fullscreen_window()

def download_video(song):
    output = './static/video.mp4'

    with download_lock:
        if os.path.isfile(output):
            os.remove(output)

        ydl_opts = {
            'outtmpl': output,
            'format': "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'ytsearch:{song} karaoke'])

    driver.get('http://127.0.0.1:8080/play_video')

if __name__ == "__main__":
    selenium_thread = threading.Thread(target=run_selenium)
    selenium_thread.start()

    app.run(host="0.0.0.0", port=8080)