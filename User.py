from typing import Any
import rsa
import yaml

class User:
    def __init__(self, name=None, ssn=None, wallet_file=None, keypair=None, data=None):
        self.name = name
        self.wallet_file = wallet_file
        self.ssn = ssn
        self.data = data
        try:
            self.wallet = yaml.safe_load(open(wallet_file, 'r+'))
        except Exception as e:
            self.wallet = {}
        if self.wallet is None:
            self.wallet = {}
        if keypair is None:
            self.keypair = rsa.newkeys(1024)
        else:
            self.keypair = keypair

    def set_data(self, data):
        self.data = data

    def encrypt_data(self):
        if self.data is not None:
            encrypted_data = rsa.encrypt(self.data.encode('utf-8'), self.keypair[0])
            return encrypted_data
        else:
            return None



		