import socket
import json
import threading
from queue import Queue
from PyQt5.QtCore import QObject, QThread



class Peer(QThread):
    def __init__(self, address="192.168.1.10", tcp_port=12345, udp_port=12346, buffer_size=1024, handler=None, parent=None):
        super(Peer, self).__init__(parent)
        self.handler = handler
        self.address = address
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.buffer_size = buffer_size
        self.is_video_started = False

        self.tcp_listen_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.tcp_listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.tcp_listen_socket.bind((self.address, self.tcp_port))
        self.tcp_listen_socket.listen(10)

    def find(self):
        print("find")
        active_clients = []
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
            for i in range(9, 1, -1):
                address = f"192.168.1.{i}"
                #address = "127.0.0.1"
                print(f"looking for address: {address}")
                try:
                    sock.connect((address, self.tcp_port))
                    print(f"after connect")
                    answer = {}
                    answer["code"] = "HELLO"
                    sock.sendall(json.dumps(answer).encode())
                    print(f"after sendall")
                    response = sock.recv(self.buffer_size)
                    print(f"after recv")
                    response = json.loads(response.decode())
                    code = response["code"]
                    if not response or code != "HELLO":
                        print(f"Address {address} is peer but not responds correctly")
                        continue
                    print(f"Address {address} is peer")
                    active_clients.append(address)
                except socket.error:
                    print(f"Address {address} is not active")
        return active_clients

    def tcp_connect(self, address, data, handler):
        # data in bytes
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
            try:
                s.connect((address, self.tcp_port))
            except OSError:
                print("tcp connection can't be established")
                raise OSError("possibly server doesn't respond")

            while True:
                s.sendall(data)
                response = s.recv(self.buffer_size)
                if not response:
                    print("no more data")
                    break
                data = handler.tcp_handler(response)
                if not data:
                    break
        self.is_video_started = self.handler.is_video_started

    def tcp_accept(self, conn, addr, handler):
        # data in bytes
        print(f"connected by {addr}")
        with conn:
            while True:
                data = conn.recv(self.buffer_size)
                print(data)
                if not data:
                    break
                response = handler.tcp_handler(data)
                if not response:
                    break
                conn.sendall(response)
        self.is_video_started = self.handler.is_video_started

    def run(self):
        self.is_active = True
        while True:
            conn, addr = self.tcp_listen_socket.accept()
            th = threading.Thread(target=self.tcp_accept,
                                  args=(conn, addr, self.handler))
            th.start()
            if not self.is_active:
                break