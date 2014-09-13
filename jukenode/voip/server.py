# -*- coding: utf-8 -*-
from gevent import monkey;  monkey.patch_all()
import gevent
from gevent.queue import JoinableQueue

import pyaudio
import socket
import time
import json
from bson import BSON, Binary, ObjectId, Timestamp, _bson_to_dict
import struct
import zmq

##import speex
##d = speex.Decoder()
##d.initialize(speex.SPEEX_MODEID_WB)
##    decdata = d.decode(buf)
##    streamout.write(decdata)
##            siz = struct.unpack("<i", frame[:4])[0]
##            dta = _bson_to_dict(frame, dict, False)
##            frame = Binary.decode(dta['byte'])

def buffer(size, data):
    buf = bytearray()
    while len(buf) < size:
        buf.append(data)
        yield None
    yield buf


class Receiver(gevent.Greenlet):
    PORT = 20000
    CHUNK = 512

    def __init__(self):
        gevent.Greenlet.__init__(self)
        self.queue = JoinableQueue()

    def _run(self):
        context = zmq.Context()
        receiver = context.socket(zmq.PULL)
        receiver.connect("tcp://localhost:%s" % self.PORT)
        print 'rcv_on'
        while True:
            frame =  receiver.recv()
            sys.stdout.write('.')
            sys.stdout.flush()

            self.queue.put(frame)
            time.sleep(0.0001)



class Speaker(gevent.Greenlet):
    RATE = 44100

    def __init__(self, rcv):
        gevent.Greenlet.__init__(self)
        self.rcv = rcv
        PA = pyaudio.PyAudio()
        self.pa= PA.open(
            format= pyaudio.paInt16,
            channels= 1,
            rate= self.RATE,
            output= True
        )
        self.queue = JoinableQueue()

    def _run(self):
        print 'spk_on'
        while True:
            try:
                buf = self.rcv.queue.get()
            except gevent.queue.Empty:
                buf = '\0'
##            print '.',
            self.pa.write(buf)
            time.sleep(0.0001)

        self.queue.task_done()
        self.pa.close()


if __name__ == '__main__':
    rcv = Receiver()
    spk = Speaker(rcv)
    rcv.start();  spk.start()
    print 'start'
    time.sleep(1000)