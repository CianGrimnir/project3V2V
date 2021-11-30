import Crypto.Cipher.AES as AES
from Crypto.PublicKey import RSA

import string
import random
from Crypto.Cipher import AES


def do_encrypt(message):
    while len(bytes(message, encoding='utf-8')) % 16 != 0:
        message = message + random.choice(string.ascii_letters)
    obj = AES.new('This is a key133', AES.MODE_CBC, 'This is an IV456')
    ciphertext = obj.encrypt(message)
    return ciphertext


def do_decrypt(ciphertext):
    obj2 = AES.new('This is a key133', AES.MODE_CBC, 'This is an IV456')
    message = obj2.decrypt(ciphertext)
    return message
