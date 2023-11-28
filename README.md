# <img width="32" alt="logo" src="https://github.com/17hoehbr/OpenMic-Karaoke/blob/main/static/icons/logo.png"> OpenMic Karaoke

OpenMic is a "KTV"-style karaoke song search and queueing system. It connects to your TV, and shows a QR code for computers and smartphones to connect to a web interface. From there, multiple users can seamlessly search karaoke tracks from YouTube. This project is heavily inspired by the [pikaraoke project](https://github.com/vicwomg/pikaraoke) but completely rewritten to use the web browser as the TV display instead of PyGame / VLC. The end goal is that this project will be simple enough to install and reliable enough that it can easily be used on Steam Decks and other Linux distros by users with no python knowledge.

Stil very early in development! Contributions appreciated, particularly for the frontend.

## Features

- Web interface for multiple users to queue tracks
- Splash screen with connection QR
- Adding new songs from Youtube
- Pause/Skip/Restart
- Queue management

## Install

Currently OpenMic is only distributed as the python script or as a Linux AppImage. Theoretically Pyinstaller should be able to build a working Windows or Mac build relatively easily but I do not have a Windows or Mac device to test the builds on. I will gladly accept any pull requests that add a Github action to build for other platforms / distributions but I don't plan on maintaining them manually.

Running from source:
1. Install dependencies

On Linux you will need to install the pywebview dependencies. For debian based distros this should cover it:
```
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1
```

For other platforms please consult the [pywebview documentation](https://pywebview.flowrl.com/guide/installation.html#dependencies).

2. Clone repository
```
git clone https://github.com/17hoehbr/OpenMic-Karaoke.git
```

3. Enter directory
```
cd OpenMic-Karaoke
```

4. Setup virtual environment
```
python -m venv .venv
```

5. Activate virtual environment
```
source .venv/bin/activate
```

6. Install python requirements
```
pip install -r requirements.txt
```

7. Run python app
```
python app.py
```

Building:

Follow steps 1-6, then run:
```
pyinstaller build.spec
```

## Screenshots

### TV

<p float="left">

  <img width="400" alt="tv1" src="https://github.com/17hoehbr/OpenMic-Karaoke/assets/1351017/009f6287-6610-4aff-afc5-e5b9f42a6148">
  <img width="400" alt="tv2" src="https://github.com/17hoehbr/OpenMic-Karaoke/assets/1351017/aac68a30-edc6-4bc1-8764-df497eb6b3da">

### Web interface

<p float="left">
<img width="250" style="float:left" alt="nowplaying" src="https://github.com/17hoehbr/OpenMic-Karaoke/assets/1351017/a1f0b2de-9ddd-4e83-8cbb-2e0ece32f259">
<img width="250" style="float:left" alt="queue" src="https://github.com/17hoehbr/OpenMic-Karaoke/assets/1351017/764b2096-6d60-41b9-923c-3f83c433110a">
<img width="250" style="float:left" alt="search" src="https://github.com/17hoehbr/OpenMic-Karaoke/assets/1351017/fcdbc19e-ec0f-4722-908a-cfc1b9bf4a04">
<img width="250" style="float:left" alt="admin" src="https://github.com/17hoehbr/OpenMic-Karaoke/assets/1351017/304af1f6-085c-4386-9bcf-9fbbdfc838d0">

<a href="https://www.flaticon.com/free-icons/microphone" title="microphone icons">Microphone icons created by Freepik - Flaticon</a>
