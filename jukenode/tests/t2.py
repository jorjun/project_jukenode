import os
import pyaudio
import struct
import time

class Spk(object):
    RATE = 44000
    CHUNK = 1000

    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.pa = pyaudio.PyAudio().open(
            format= pyaudio.paInt8,
            channels= 1,
            rate= self.RATE,
            output= True
        )
        return self

    def __exit__(self , type, value, traceback):
        self.pa.close()
        if  traceback:
            print(traceback)

    def get_chunk(self):
        with open(self.filename, "rb") as wav:
            #chunk = wav.read(72)
            while True:
                chunk = wav.read(self.CHUNK)
                unpack = lambda fmt, x, y: struct.unpack(fmt, chunk[x: y])[0]
                if chunk:
                    #o16 = bytes(chunk[1::2])
                    yield bytes(chunk)
                else:
                    break

    def play(self):
        for chunk in self.get_chunk():
            self.pa.write(chunk)

    def write(self, filename):
        with open(filename, "wb") as wav8:
            for byte in self.get_chunk():
                wav8.write(byte)
        print('conversion complete: %s' % filename)

if __name__ == "__main__":
    #with Spk(filename="sound1.wav") as spk:
        ##spk.play()
        #spk.write("sound8.wav")

    with Spk(filename="sound8.wav") as spk:
        start = time.time()
        spk.play()
        print (time.time() - start)
        #spk.write("sound8.wav")
