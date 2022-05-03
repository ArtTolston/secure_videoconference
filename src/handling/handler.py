import json
from cryptography.cryptography import Crypto

class Handler:
    def __init__(self, crypto=None):
        if crypto is None:
            crypto = Crypto()
        self.crypto = crypto

    def tcp_handler(self, data):
        response = {}
        data = data.decode()
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
                encrypted_key = self.crypto.rsa_encrypt_session_key(data["pub_key"])
                response["code"] = "START2"
                response["algorithm"] = "PKI"
                response["encrypted_key"] = encrypted_key
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
                session_key = self.crypto.rsa_decrypt_session_key(data["encrypted_key"])
                self.crypto.set_session_key(session_key)
                response["code"] = "OK"
        elif code == "END":
            print("END")
            response["code"] = "OK"
        else:
            pass
        print(response)
        return json.dumps(response).encode()
