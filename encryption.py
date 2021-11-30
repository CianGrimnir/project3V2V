
# uses pycryptodome package 
import Crypto.Cipher.AES as AES
from Crypto.PublicKey import RSA

import string
import random
#from Crypto.Cipher import AES
import base64
from Crypto import Random
import os, hashlib


BLOCK_SIZE = 16
padding = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpadding = lambda s: s[:-ord(s[len(s) - 1:])]


def do_encrypt(message):
    # IV = hashlib.md5(os.urandom(128)).hexdigest()[:16]
    IV = Random.new().read(AES.block_size)
    cipher = AES.new('abcd1234efgh5678'.encode("utf8"), AES.MODE_CBC, IV)
    message = padding(message)
    #ciphertext = cipher.encrypt(message)
    encrypted_message = cipher.encrypt(message.encode("utf-8"))
    ciphertext = base64.b64encode(IV + encrypted_message)
    return ciphertext


def do_decrypt(ciphertext):
    enc = base64.b64decode(ciphertext)
    iv = enc[:16]
    #IV = hashlib.md5(os.urandom(128)).hexdigest()[:16]
    cipher = AES.new('abcd1234efgh5678'.encode("utf8"), AES.MODE_CBC, iv)
    message = unpadding(cipher.decrypt(enc[16:]))
    #message = unpadding(cipher.decrypt(ciphertext))
    return message.decode("utf8")
