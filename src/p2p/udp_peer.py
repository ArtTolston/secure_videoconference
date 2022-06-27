import socket
import json
import threading
from queue import Queue
from PyQt5.QtCore import QObject, QThread
import sys
import zlib


class UDP_Peer(QThread):
    def __init__(self, address="192.168.1.10", udp_port=12346, buffer_size=8192, handler=None, parent=None):
        super(UDP_Peer, self).__init__(parent)
        self.handler = handler
        self.address = address
        self.udp_port = udp_port
        self.buffer_size = buffer_size
        self.choosed_address = "192.168.1.9"
        self.is_video_started = True

        self.udp_listen_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_listen_socket.bind((self.address, self.udp_port))

        # threadsafe queues to extract data from class in parallel
        self.udp_receive_queue = Queue()
        self.udp_send_queue = Queue()

    def udp_start(self):
        # data should be in bytes b''
        print("inside udp_start")
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as udp_sock:
            udp_sock.sendto(b'START', (self.choosed_address, self.udp_port))

    def udp_stop(self):
        # data should be in bytes b''
        print("inside udp_stop")
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as udp_sock:
            udp_sock.sendto(b'STOP', (self.choosed_address, self.udp_port))


    def run(self):
        i = 0
        image = b''
        print(f"start udp server listen on\n [address: {self.address}, port: {self.udp_port}]")
        while True:
            recv_data, addr = self.udp_listen_socket.recvfrom(self.buffer_size)
            if not recv_data:
                print("no recv_data")
                break
            if recv_data == b'START':
                self.choosed_address = addr[0]
                print(f"sent by address: {addr[0]} from port: {addr[1]}")
            elif recv_data == b'STOP':
                self.is_video_started = False
                self.udp_send_queue = Queue()
            else:
                image += recv_data
                print(f"recv_data size: {len(recv_data)}")
                print(f"image size: {len(image)}")
                if len(recv_data) < self.buffer_size:
                    image = zlib.decompress(image)
                    self.udp_receive_queue.put(image)
                    image = b''

            if i == 0:
                data = self.udp_send_queue.get()
                if data == b'STOP':
                    self.udp_send_queue = Queue()
                    print("goodbye")
                    return
                zdata = zlib.compress(data)
                print(f"zdata size: {len(zdata)}")

            if i + self.buffer_size > len(zdata):
                send_data = zdata[i:]
                i = 0
            else:
                print(i)
                send_data = zdata[i: i + self.buffer_size]
                i += self.buffer_size
            print("udp server send")
            self.udp_listen_socket.sendto(send_data, (self.choosed_address, self.udp_port))
