from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
from math import ceil


cryptor = AES.new(get_random_bytes(32), AES.MODE_CBC)


def encode(txt: str, length=32):
    return txt.rjust(ceil(len(txt)/length)*length, " ").encode("ascii")


print(cryptor.decrypt(cryptor.encrypt(encode("ok"))))
