import socket
import qrcode
import threading
from yt_dlp import YoutubeDL
from flask import Flask, render_template, request, redirect
from selenium import webdriver
from selenium.webdriver.common.by import By

app = Flask(__name__)

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

@app.route("/search")
def search():
    return render_template("search.html", active="search")


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
    song = "under pressure"

    output = './static/video.mp4'

    ydl_opts = {
        'outtmpl': output,  # Set the output filename and path
        'format': "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f'ytsearch:{song} karaoke'])

    return render_template("video_player.html")

def run_selenium():
    global driver
    driver = webdriver.Firefox()
    driver.get('http://127.0.0.1:8080/tv')

if __name__ == "__main__":
    selenium_thread = threading.Thread(target=run_selenium)
    selenium_thread.start()

    app.run(host="0.0.0.0", port=8080)