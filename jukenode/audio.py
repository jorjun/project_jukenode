import os
import pyaudio
import struct
import time


class Sound(object):
    CHUNK = 2000

    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, "rb") as wav:
            _wav_hdr = wav.read(38)
            unpack = lambda fmt, x, y: struct.unpack(fmt, _wav_hdr[x:y])[0]
            self.sample_rate = unpack('<L', 24, 28)
            self.channels = unpack('<H', 22, 24)
            self.align = unpack('<H', 32, 34)
            self.bps =  unpack('<H', 34, 36)  # Bits per sample: 8/16

            self.file_size = wav.seek(0, 2)

            self.data_offset = 12
            while self.data_offset < self.file_size:
                wav.seek(self.data_offset)
                chunk_h = wav.read(8)
                self.chunk_size = struct.unpack('<L', chunk_h[4:8])[0]
                if chunk_h[0:4] == b'data':
                    break
                self.data_offset += 8 + self.chunk_size

    def __enter__(self):
        self.pa = pyaudio.PyAudio().open(
            format= pyaudio.paInt8,
            channels = self.channels,
            rate= self.sample_rate,
            output= True
        )
        return self

    def __exit__(self , type, value, traceback):
        self.pa.close()
        if  traceback:
            print(traceback)

    def __iter__(self):
        with open(self.filename, "rb") as wav:
            wav.seek(self.data_offset)
            while True:
                chunk = wav.read(self.CHUNK)
                if chunk:
                    if self.bps == 16:
                        yield bytes(chunk[1::2])  # 8 bits
                    else:
                        yield bytes(chunk)
                else:
                    raise StopIteration


    def play(self):
        for chunk in self:
            self.pa.write(chunk)

    def write(self, filename):
        with open(filename, "wb") as wav8:
            for byte in self.get_chunk():
                wav8.write(byte)
        print('conversion complete: %s' % filename)

if __name__ == "__main__":
    with Sound(filename="tests/sound1.wav") as spk:
    #with Sound(filename="/Volumes/NO NAME/sound8.wav") as spk:

        spk.play()
        #spk.write("sound8.wav")

    #with Sound("/Volumes/NO NAME/sound8.wav") as spk:
        #start = time.time()
        #spk.play()
        #print (time.time() - start)
        #spk.write("/Volumes/NO NAME/sound8.wav")
