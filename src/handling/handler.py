import json
from src.handling.cryptography.cryptography import Crypto
from base64 import b64encode, b64decode


class Handler(QObject):
    def __init__(self, crypto=None):
        if crypto is None:
            crypto = Crypto()
        self.crypto = crypto
        self.is_video_started = False

    def get_crypto(self):
        return self.crypto

    def tcp_handler(self, data):
        response = {}
        data = json.loads(data.decode())
        print(data)
        code = data["code"]
        if code == "HELLO":
            print("HELLO")
            response["code"] = "HELLO"
            return json.dumps(response).encode()
        elif code == "START1":
            algorithm = data["algorithm"]
            if algorithm == "DH":
                print("START1 DH")
                self.crypto.gen_dh_shared_key(data["pub_key"])
                self.crypto.gen_session_key_from_shared_key()
                pub_key = self.crypto.gen_dh_pub_key()
                response["code"] = "START2"
                response["algorithm"] = "DH"
                response["pub_key"] = pub_key
            elif algorithm == "PKI":
                print("START1 PKI")
                # if exists, doesn't change
                self.crypto.gen_session_key()
                encrypted_key = self.crypto.rsa_encrypt_session_key(data["pub_key"].encode())
                response["code"] = "START2"
                response["algorithm"] = "PKI"
                response["encrypted_key"] = b64encode(encrypted_key).decode()
                print(f"response: {response}")
            else:
                pass
        elif code == "START2":
            algorithm = data["algorithm"]
            if algorithm == "DH":
                print("START2 DH")
                self.crypto.gen_dh_shared_key(data["pub_key"])
                self.crypto.gen_session_key_from_shared_key()
                response["code"] = "OK"
            elif algorithm == "PKI":
                print("START2 PKI")
                session_key = self.crypto.rsa_decrypt_session_key(b64decode(data["encrypted_key"].encode()))
                self.crypto.set_session_key(session_key)
                response["code"] = "OK"
        elif code == "OK":
            print("OK")
            self.is_video_started = True
            return
        else:
            pass
        print(response)
        return json.dumps(response).encode()
