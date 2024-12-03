import os
import re
import threading
import random
import json
import glob
from settings import port
from yt_dlp import YoutubeDL
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

app.secret_key = os.urandom(12).hex()

song_queue = []

cwd = os.path.dirname(__file__)
song_dir = f"{cwd}/songs"

if not os.path.isdir(song_dir):
    os.mkdir(song_dir)

# Mobile Routes

@app.route("/")
def index():
    if len(song_queue) >= 1:
        now_playing = song_queue[0]["title"]
    else:
        now_playing = 'Nothing is currently playing'

    if len(song_queue) >= 2:
        next_song = song_queue[1]["title"]
    else:
        next_song = 'Nothing is currently queued'

    return render_template("mobile/index.html", active="home", now_playing=now_playing, next_song=next_song)

@app.route("/queue")
def queue():
    return render_template("mobile/queue.html", active="queue", song_queue=song_queue )

@app.route("/search", methods=['GET', 'POST'])
def search():
    result = ''
    if request.method == 'POST':
        try:
            if 'search' in request.form:
                song = request.form['search']
                num_results = 5
                yt_search = f'ytsearch{num_results}:"{song} karaoke"'

                ydl_opts = {
                    'format': 'best',
                    'extract_flat': True,
                    'extract_no_playlists': True
                }

                with YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(yt_search, download=False)

                for r in result['entries']:
                    r['title'] = r['title'].replace("'", "")

        except Exception as e:
            print(f"Error during search: {e}")

    return render_template("mobile/search.html", active="search", result=result)

@app.route("/admin")
def admin():
    return render_template("mobile/admin.html", active="admin")

# Mobile Web Socket Listeners

@socketio.on('start_download', namespace='/')
def start_download(video_id, video_title, username):
    # removes (Karaoke - Version) from title
    video_title = re.sub(r'\s*\(.*\)|\'', '', video_title)
    
    song_queue.append({'id': video_id, 'title': video_title, 'user': username})

    if len(song_queue) == 1:
        socketio.emit('play_video', namespace='/tv')

    if not os.path.isfile(f'{song_dir}/{video_id}.mp4'):
        ydl_opts = {
            'outtmpl': f'{song_dir}/{video_id}.mp4',
            'format': "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]",
            'writeinfojson': True
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(video_id)
        except Exception as e:
            print(f"Error during video download: {e}")

# admin controls
@socketio.on('player_restart', namespace='/')
def player_restart():
    socketio.emit('player_restart', namespace='/tv')

@socketio.on('player_pause', namespace='/')
def player_pause():
    socketio.emit('player_pause', namespace='/tv')

@socketio.on('player_skip', namespace='/')
def player_skip():
    socketio.emit('player_skip', namespace='/tv')

# queue controls
@socketio.on('move_up', namespace='/')
def move_up(data):
    pos1 = int(data)
    pos2 = pos1 - 1

    song_queue[pos1], song_queue[pos2] = song_queue[pos2], song_queue[pos1]

@socketio.on('move_down', namespace='/')
def move_down(data):
    pos1 = int(data)
    pos2 = pos1 + 1

    song_queue[pos1], song_queue[pos2] = song_queue[pos2], song_queue[pos1]

@socketio.on('del_song', namespace='/')
def del_song(data):
    song_queue.pop(data)

# only queues songs that are already downloaded
@socketio.on('queue_random', namespace='/')
def queue_random(username):
    songs = glob.glob(f'{song_dir}/*.mp4')
    
    songs_random = []

    if songs:
        for i in range(0, 5):
            songs_random.append(random.choice(songs))

        for i in songs_random:
            song = i.split('.')[0]
            with open(f'{song}.info.json') as json_data:
                data = json.load(json_data)

            song_queue.append({'id': data['id'], 'title': data['title'], 'user': username})

            if len(song_queue) <= 5:
                socketio.emit('play_video', namespace='/tv')

def main():
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()