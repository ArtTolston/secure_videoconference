import socket
from queue import Queue

class Peer:
    def __init__(self, address="127.0.0.1", tcp_port=10000, udp_port=10001, buffer_size=1024):
        self.address = address
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.buffer_size = buffer_size
        self.tcp_listen_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.tcp_listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.udp_listen_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_send_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # threadsafe queues to extract data from class in parallel
        self.tcp_queue = Queue()
        self.udp_receive_queue = Queue()
        self.udp_send_queue = Queue()

    def find(self):
        active_clients = []
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
            for i in range(10):
                address = f"192.168.1.{i}"
                try:
                    sock.connect((address, self.tcp_port))
                    sock.sendall(b"Hello")
                    data = sock.recv(self.buffer_size)
                    if not data or data is not b"Hello":
                        print(f"Address {address} is peer but not responds correctly")
                        continue
                    print(f"Address {address} is peer")
                    active_clients.append(address)
                except socket.error:
                    print(f"Address {address} is not active")
        return active_clients

    def udp_send(self, address, data):
        # data should be in bytes b''
        self.udp_send_socket.sendto(data, (address, self.udp_port))

    def udp_receive(self):
        # receive data in bytes
        while True:
            data, addr = self.udp_listen_socket.recv(self.buffer_size)
            if not data:
                break
            self.udp_put_receive_queue(data)
        print(f"connected by {addr}")
        return data

    def tcp_send(self, address, data):
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
            s.connect((address, self.tcp_port))
            s.sendall(data)

    def tcp_receive(self):
        conn, addr = self.tcp_listen_socket.accept()
        print(f"connected by {addr}")
        with conn:
            while True:
                data = conn.recv(self.buffer_size)
                if not data:
                    break
                self.tcp_put_queue(data)


    def udp_put_receive_queue(self, data):
        self.udp_receive_queue.put(data)

    def udp_get_receive_queue(self):
        return self.udp_receive_queue.get()

    def udp_put_send_queue(self, data):
        self.udp_send_queue.put(data)

    def udp_get_send_queue(self):
        return self.udp_send_queue.get()

    def tcp_put_queue(self, data):
        self.tcp_queue.put(data)

    def tcp_get_queue(self):
        return self.tcp_queue.get()

    def run(self):
        self.tcp_listen_socket.bind((self.address, self.tcp_port))
        self.udp_listen_socket.bind((self.address, self.udp_port))