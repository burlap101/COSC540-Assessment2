# The purpose of this file is to setup the client protocol for client cryptograpy. It works
# a pre and post processing block attached to the original client for incoming and outgoing messages.
# It achieves this by setting itself up as another host on the loopback network interface.

from crypto import CryptoCommon
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


class ClientCrypto(CryptoCommon):

    def __init__(self):
        print('Retrieving server RSA public key')
        self.server_rsa_pubkey = self.retrieve_server_pubkey()
        print('Generating Diffie-Hellman key pair')
        self.dh_pubkey = self.generate_dh_keypair()
        print('Crypto initialising complete')


    def retrieve_server_pubkey(self):
        with open('.keys/bshipserverpub.pem', 'rb') as kf:
            server_rsa_pubkey = serialization.load_pem_public_key(
                kf.read(),
                backend=default_backend()
            )
            return server_rsa_pubkey

    def encrypt_msg_rsa(self, message):
        ciphertext = self.server_rsa_pubkey.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    def verify_server_dh_pubkey(self, signeddh):
        # the server has sent a Diffie-Hellman public key along with a signature
        # generated using the server's private RSA key using the DH key and hashed SHA-2.
        # This method now determines if the sent key was from the server by verifying the signature.
        # An InvalidSignature exception is raised if the verification fails
        server_dh_pubkey = signeddh[:signeddh.find(b'-----END PUBLIC KEY-----\n')+len(b'-----END PUBLIC KEY-----\n')]
        signature = signeddh[signeddh.find(b'-----END PUBLIC KEY-----\n')+len(b'-----END PUBLIC KEY-----\n'):]

        self.server_rsa_pubkey.verify(
            signature,
            server_dh_pubkey,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # if no exception raised then DH key is forwarded onto setup_fernet
        self.setup_fernet(server_dh_pubkey)