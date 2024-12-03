import sys
import socket
import qrcode
import json
import socketio
from settings import port
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

# SocketIO client to handle connection with Flask-SocketIO server
class SocketIOClient(QObject):
    message_received = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.sio = socketio.Client()
        self.sio.on('connect', self.on_connected)
        self.sio.on('message', self.on_message_received)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.connect(url)

    def on_connected(self):
        print("SocketIO connected!")
        self.sio.send("Hello from client!")

    def on_message_received(self, message):
        print(f"Message received: {message}")
        self.message_received.emit(message)

    def on_disconnect(self):
        print("SocketIO disconnected!")

    def send_message(self, message):
        self.sio.send(message)

    def close(self):
        self.sio.disconnect()

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenMic Karaoke")

        layout = QVBoxLayout()

        header = QLabel("OpenMic Karaoke")
        font = header.font()
        font.setPointSize(24)
        header.setFont(font)
        header.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )

        local_ip = self.generate_qr_code()
        qrwidget = QLabel()
        qrwidget.setPixmap(QPixmap('qr.jpg'))
        qrwidget.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )

        ipaddr = QLabel(f"http://{local_ip}:{port}")
        font = ipaddr.font()
        font.setPointSize(20)
        ipaddr.setFont(font)
        ipaddr.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )

        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(qrwidget)
        layout.addWidget(ipaddr)

        # Set central widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # SocketIO client setup
        self.socketio_client = SocketIOClient(f"http://localhost:{port}")
        self.socketio_client.message_received.connect(self.handle_text_message_received)

    def generate_qr_code(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.0.0.0", 0))
        local_ip = s.getsockname()[0]
        qr = qrcode.make(f'http://{local_ip}:{port}')
        qr.save(f"./qr.jpg")
        return local_ip

    def start(self):
        # You can send a message to the server once connected
        self.socketio_client.send_message("Hello, WebSocket server!")

    def handle_text_message_received(self, message):
        data = json.loads(message)
        if data == 'play_video':
            w = PlayerWindow()
            w.show()

        print(data)

    def send_message(self, message):
        self.socketio_client.send_message(message)

class PlayerWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("PlayerWindow")
        layout.addWidget(self.label)
        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # Start SocketIO connection
    window.start()

    app.exec()

if __name__ == "__main__":
    main()
