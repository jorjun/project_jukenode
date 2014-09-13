from pyb import DAC
import pyb
import math
import time


def play_wav(filename, chunksize=3096, freq=44100):
    dac = DAC(1)
    delay_ms = int(chunksize / (freq / 1000000))
    micros = pyb.Timer(2, prescaler=83, period=0x3fffffff)
    start = time.time()
    with open(filename, "rb") as wav:
        chunk = wav.read(chunksize)
        buf = bytearray(chunk)
        while chunk:
            micros.counter(0)
            dac.write_timed(buf, freq, mode=DAC.NORMAL)
            chunk = wav.read(chunksize)
            buf = bytearray(chunk)
            while micros.counter() < delay_ms:
                pyb.wfi()

    dac = DAC(1)
    print (time.time() - start)


def beep(delay=500):
    dac = DAC(1)
    buf = bytearray(100)
    for i in range(len(buf)):
        buf[i] = 128 + int(127 * math.sin(2 * math.pi * i / len(buf)))

    dac.write_timed(buf, 5000, mode=DAC.CIRCULAR)
    pyb.delay(1000)

