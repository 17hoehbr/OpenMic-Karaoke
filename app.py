import socket
import qrcode
import os
import re
import threading
import webview
from yt_dlp import YoutubeDL, utils
from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key = os.urandom(12).hex()

song_queue = []
song_dict = {}

port = '8080'
song_dir = "./songs"

# ---------------- Functions ----------------

def search_youtube(yt_search):
    ydl_opts = {
        'format': 'best',   # You can specify the format you want
        'extract_flat': True,
        'extract_no_playlists': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(yt_search, download=False)
        except utils.DownloadError as e:
            if "[Errno 101] Network is unreachable" in str(e):
                print("Network is unreachable. Please check your internet connection.")
            else:
                print("Download error")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    
    return result

# ---------------- Mobile Routes ----------------

@app.route("/")
def index():
    if len(song_queue) >= 1:
        now_playing = song_dict[song_queue[0]]
    else:
        now_playing = 'Nothing is currently playing'

    if len(song_queue) >= 2:
        next_song = song_dict[song_queue[1]]
    else:
        next_song = 'Nothing is currently queued'

    return render_template("mobile_index.html", active="home", now_playing=now_playing, next_song=next_song)

@app.route("/queue")
def queue():
    return render_template("queue.html", active="queue", song_dict=song_dict, song_queue=song_queue)

@app.route("/search", methods=['GET', 'POST'])
def search():
    result = ''
    if request.method == 'POST':
        try:
            if 'search' in request.form:
                song = request.form['search']
                num_results = 5
                yt_search = f'ytsearch{num_results}:"{song} karaoke"'
                result = search_youtube(yt_search)
        except Exception as e:
            print(f"Error during search: {e}")

    return render_template("search.html", active="search", result=result)

@app.route("/admin")
def admin():
    return render_template("admin.html", active="admin")

# ---------------- TV Routes ----------------

@app.route("/tv")
def tv():
    # get local ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.0.0.0", 0))

    local_ip = s.getsockname()[0]
    qr = qrcode.make(local_ip)
    qr.save("./static/qrcode.png")

    return render_template("tv_index.html", local_ip=local_ip)

@app.route('/play_video')
def play_video():
    next_song = song_queue[0]
    return render_template("video_player.html", next_song=next_song)

@app.route('/songs/<path:filename>')
def serve_video(filename):
    return send_from_directory(f'{song_dir}', filename)

# ---------------- Web Socket Listeners ----------------

@socketio.on('start_download')
def start_download(data):
    video_id = data['video_id']
    video_metadata = search_youtube(video_id)
    video_title = re.sub(r'\s*\(.*\)', '', video_metadata['title'])

    song_dict.update({video_id: video_title})
    song_queue.append(video_id)

    if not os.path.isfile(f'{song_dir}/{video_id}.mp4'):
        ydl_opts = {
            'outtmpl': f'{song_dir}/{video_id}.mp4',
            'format': "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(video_id)
        except Exception as e:
            print(f"Error during video download: {e}")
            
    socketio.emit('play_video', namespace='/tv')

@socketio.on('connect', namespace='/')
def mobile_connect():
    print("Mobile client connected")

@socketio.on('connect', namespace='/tv')
def tv_connect():
    print("TV client connected")
    if song_queue:
        socketio.emit('play_video', namespace='/tv')

@socketio.on('player_restart', namespace='/')
def player_restart():
    socketio.emit('player_restart', namespace='/tv')

@socketio.on('player_pause', namespace='/')
def player_pause():
    socketio.emit('player_pause', namespace='/tv')

@socketio.on('player_skip', namespace='/')
def player_skip():
    socketio.emit('player_skip', namespace='/tv')

@socketio.on('song_ended', namespace='/tv')
def song_ended():
    song_queue.pop(0)

@socketio.on('move_up', namespace='/')
def move_up(data):
    print(data)
    try:
        pos1 = song_queue.index(data)
        pos2 = pos1 - 1

        song_queue[pos1], song_queue[pos2] = song_queue[pos2], song_queue[pos1]
    except:
        print("error moving item")

@socketio.on('move_down', namespace='/')
def move_down(data):
    print(data)
    try:
        pos1 = song_queue.index(data)
        pos2 = pos1 + 1

        song_queue[pos1], song_queue[pos2] = song_queue[pos2], song_queue[pos1]
    except:
        print("error moving item")

@socketio.on('del_song', namespace='/')
def song_ended(data):
    song_queue.remove(data)

if __name__ == "__main__":
    thread = threading.Thread(target=lambda: socketio.run(app, host="0.0.0.0", port=port))
    thread.daemon = True
    thread.start()

    window = webview.create_window('Karaoke', 'http://127.0.0.1:8080/tv')
    webview.start(gui='gtk', debug=True)
    