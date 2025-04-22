import socket
import os
import threading
from gi.repository import GLib
from fabric.utils import idle_add

class SocketListener:
    def __init__(self, socket_path="/tmp/hyprland_socket"):
        self.socket_path = socket_path
        self.commands = {}

        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.socket_path)
        self.server.listen(1)

        print(f"Socket Listener ready : {self.socket_path}")

    def add_command(self, command, func):
        self.commands[command] = func
        print(f"Command added : {command}")

    def start(self):
        def socket_thread():
            try:
                while True:
                    conn, _ = self.server.accept()
                    data = conn.recv(1024).decode("utf-8").strip()
                    
                    if data in self.commands:
                        idle_add(self.commands[data])
                        # self.commands[data]
                    conn.close()
            finally:
                self.server.close()
                if os.path.exists(self.socket_path):
                    os.remove(self.socket_path)

        t = threading.Thread(target=socket_thread, daemon=True)
        t.start()

    def stop(self):
        self.server.close()
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)



