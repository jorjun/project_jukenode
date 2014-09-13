import sys, time

from www.jukenode.voip  import device

if __name__ == '__main__':
    spk = device.Speaker()
    spk.start()
    while not spk.is_quit():
        time.sleep(2)