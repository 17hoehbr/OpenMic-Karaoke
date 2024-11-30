import sys
import socket
import qrcode
import json
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

port = 8080

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.websocket = QWebSocket()
        self.websocket.textMessageReceived.connect(self.handle_text_message_received)
        self.websocket.connected.connect(self.handle_connected)

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

    def generate_qr_code(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.0.0.0", 0))
        local_ip = s.getsockname()[0]
        qr = qrcode.make(f'http://{local_ip}:{port}')
        qr.save(f"./qr.jpg")
        return local_ip
    
    def start(self):
        url = f"wss://localhost:{port}"
        self.websocket.open(url)

    def handle_connected(self):
        print("Websocket connected")

    def handle_text_message_received(self, message):
        data = json.loads(message)
        if data == 'play_video':
            w = PlayerWindow()
            w.show()

        print(data)

    def send_message(self, message):
        self.websocket.sendTextMessage(message)

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


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()