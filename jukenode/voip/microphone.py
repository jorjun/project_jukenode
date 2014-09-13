import sys, time

from www.jukenode.voip import device


if __name__ == '__main__':
##    mic = device.Microphone(dest="192.168.1.112", record_seconds=100)
    mic = device.Microphone(dest="192.168.0.48", record_seconds=100)
    mic.start()
    while not mic.is_quit():
        time.sleep(2)
