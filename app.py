import socket
import qrcode
import threading
from yt_dlp import YoutubeDL
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['player_control'] == 'restart':
            pass # do something
        elif request.form['player_control'] == 'pause':
            v = driver.find_element(By.ID, 'video')

        elif request.form['player_control'] == 'skip':
            pass # do something else
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

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def run_selenium():
    # Start Selenium WebDriver after Flask server has started
    global driver
    driver = webdriver.Firefox()
    driver.get('http://127.0.0.1:8080/tv')


if __name__ == "__main__":
    # Start Flask in the main thread
    flask_server = threading.Thread(target=run_flask)
    flask_server.start()

    frontend = threading.Thread(target=run_selenium)
    frontend.start()
