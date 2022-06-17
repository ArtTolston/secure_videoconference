from queue import Queue
import json
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from pyDH import DiffieHellman
from base64 import b64decode, b64encode


class Crypto:
    def __init__(self, session_key=get_random_bytes(16)):
        # AES
        self.AES = "AES"
        self.session_key = session_key
        # Diffie-Hellman
        self.DH = DiffieHellman()
        self.DH_shared_key = None
        self.DH_pub_key = None
        # Public-key cryptography
        key = RSA.generate(2048)
        self.RSA_private_key = key.export_key()
        self.RSA_public_key = key.public_key().export_key()
        self.RSA_cipher = PKCS1_OAEP.new(key)

    def aes_encrypt(self, data):
        # data should be in bytes
        aes = AES.new(self.session_key, AES.MODE_CBC)
        encrypted_bytes = aes.encrypt(pad(data, AES.block_size))
        encrypted_bytes = b64encode(encrypted_bytes)
        iv = aes.iv
        iv = b64encode(iv)
        data_to_send = json.dumps({"iv": iv, "encrypted_bytes": encrypted_bytes}).encode()
        return data_to_send

    def aes_decrypt(self, data):
        # data should be in bytes
        aes = AES.new(self.session_key, AES.MODE_CBC)
        data = data.decode()
        iv = data["iv"]
        aes.iv = b64decode(iv)
        encrypted_bytes = data["encrypted_bytes"]
        encrypted_bytes = b64decode(encrypted_bytes)
        data_to_show = unpad(aes.decrypt(encrypted_bytes), AES.block_size)
        return data_to_show

    def gen_dh_shared_key(self, pub_key):
        self.DH_shared_key = self.DH.gen_shared_key(pub_key)

    def gen_dh_pub_key(self):
        self.DH_pub_key = self.DH.gen_public_key()
        return self.DH_pub_key

    def gen_session_key_from_shared_key(self):
        hash_object = SHA256.new(self.DH_shared_key.encode())
        hash_object.digest_size = 16
        self.session_key = hash_object.digest()

    def set_session_key(self, key):
        self.session_key = key

    def gen_session_key(self):
        if self.session_key is None:
            self.session_key = get_random_bytes(16)

    def rsa_encrypt_session_key(self, rsa_pub_key):
        rsa_pub_key = RSA.import_key(rsa_pub_key)
        new_cipher = PKCS1_OAEP.new(rsa_pub_key)
        return new_cipher.encrypt(self.session_key)

    def rsa_decrypt_session_key(self, data):
        print(data)
        return self.RSA_cipher.decrypt(data)

    def rsa_get_pub_key(self):
        return self.RSA_public_key
