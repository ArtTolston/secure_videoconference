import socket
import json
import threading
from queue import Queue
from PyQt5.QtCore import QObject, QThread
import sys
import zlib

class UDP_Peer(QThread):
    def __init__(self, address="192.168.1.10", udp_port=12346, buffer_size=1024, handler=None, parent=None):
        super(UDP_Peer, self).__init__(parent)
        self.handler = handler
        self.address = address
        self.udp_port = udp_port
        self.buffer_size = buffer_size
        self.choosed_address = "192.168.1.9"

        self.udp_listen_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_listen_socket.bind((self.address, self.udp_port))

        # threadsafe queues to extract data from class in parallel
        self.udp_receive_queue = Queue()
        self.udp_send_queue = Queue()



    def run(self):
        # data should be in bytes b''
        i = 0
        image = b''
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as udp_sock:
            while True:
                if i == 0:
                    data = self.udp_send_queue.get()
                    zdata = zlib.compress(data, zlib.Z_BEST_SPEED)
                    print(sys.getsizeof(zlib.compress(data, zlib.Z_BEST_SPEED)))

                if i + 1000 > len(zdata):
                    send_data = zdata[i:]
                    i = 0
                else:
                    print(i)
                    send_data = zdata[i: i + 1000]
                    i += 1000
                udp_sock.sendto(send_data, (self.choosed_address, self.udp_port))

                print("between send and recv")

                recv_data = udp_sock.recvfrom(self.buffer_size)
                if not recv_data:
                    print("no recv_data")
                    break

                image += recv_data
                if len(recv_data) < 1000:
                    image = zlib.decompress(image, zlib.Z_BEST_SPEED)
                    self.udp_receive_queue.put(image)
                    image = b''




    def udp_receive(self):
        # receive data in bytes
        while True:
            data, addr = self.udp_listen_socket.recv(self.buffer_size)
            if not data:
                break
            self.udp_put_receive_queue(data)
        print(f"connected by {addr}")
        return data

