import os
import pyaes
import binascii
import pbkdf2
import secrets


class Crypt:
    def __init__(self, password, salt=None, iv=None):
        if salt is None:
            self.salt = os.urandom(16)
        else:
            self.salt = salt
        if iv is None:
            self.iv = secrets.randbits(256)
        else:
            self.iv = iv
        self.psswd = password
        self.key = pbkdf2.PBKDF2(self.psswd, self.salt).read(32)

    def encrypt(self, pt):
        aes = pyaes.AESModeOfOperationCTR(self.key, pyaes.Counter(self.iv))
        ct = list(aes.encrypt(pt))
        out = ""
        for num in ct:
            hexed = hex(num)[2:]
            out += hexed.zfill(2)

        return out

    def decrypt(self, ct):
        ct = bytes([int(ct[i:i+2], 16) for i in range(0, len(ct), 2)])
        aes = pyaes.AESModeOfOperationCTR(self.key, pyaes.Counter(self.iv))
        return aes.decrypt(ct).decode()


if __name__ == '__main__':
    c = Crypt("1234", "1234")
    t = c.encrypt("self.__init__(\"1234\")")
    print(t)
    print(c.decrypt(t))
