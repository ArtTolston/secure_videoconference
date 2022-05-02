from queue import Queue
import json
from crypto.Cipher import AES
from crypto.Util.Padding import pad, unpad


class Crypto:
    def __init__(self, session_key=None):
        self.AES = "AES"
        self.session_key = session_key

    def encrypt(self, in_data_f, out_data_f):
        # data should be in bytes
        aes = AES.new(self.session_key, AES.MODE_CBC)
        while True:
            data = in_data_f()
            if not data:
                break
            encrypted_bytes = aes.encrypt(pad(data, AES.block_size))
            iv = aes.iv
            data_to_send = json.dumps({"iv": iv, "encrypted_bytes": encrypted_bytes}).encode()
            out_data_f(data_to_send)

    def decrypt(self, in_data_f, out_data_f):
        # data should be in bytes
        aes = AES.new(self.session_key, AES.MODE_CBC)
        while True:
            data = in_data_f()
            if not data:
                break
            data = data.decode()
            aes.iv = data["iv"]
            encrypted_bytes = data["encrypted_bytes"]
            data_to_send = unpad(aes.decrypt(encrypted_bytes), AES.block_size)
            out_data_f(data_to_send)