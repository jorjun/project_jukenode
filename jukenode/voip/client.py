# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()
import gevent
from gevent.queue import JoinableQueue

import time
import pyaudio
from io import BytesIO

import socket, sys
from bson import BSON, Binary, ObjectId, Timestamp, _bson_to_dict
import struct
import zmq


##import speex
#from speex import SPEEX_SET_QUALITY
#from speex import SPEEX_SET_VBR
#e = speex.Encoder()
#e.initialize(speex.SPEEX_MODEID_WB)
##        encdata = e.encode(string_audio_data)
##        s.sendto(encdata,ADDR)
#    quality=input('Please enter a quality [0-10]:')
#    e.control(SPEEX_SET_QUALITY, int(quality))
##            dta ={ 'byte' : Binary(frame) }
##            bson = BSON.encode(dta)


class  Encoder(object):
    def __init__(self):
        self.buf = []
        self.idx = 0

    def push(self, byte):
        pass


class Transmitter(gevent.Greenlet):
    PORT = 20000

    def __init__(self, mic):
        gevent.Greenlet.__init__(self)
        self.mic = mic

    def _run(self):
        context = zmq.Context()
        sender = context.socket(zmq.PUSH)
        sender.connect ("tcp://localhost:%s" % self.PORT)
        print 'trn_on'
        start = time.time()
        while True:
            frame = self.mic.queue.get()
            sender.send(frame)
            time.sleep(0.0001)
            sys.stdout.write('.')
            sys.stdout.flush()
            self.mic.queue.task_done()

            if time.time() - start > self.mic.record_seconds:
                print 'timed trn'
            break


class Microphone(gevent.Greenlet):
    CHUNK = 512
    RATE = 44100
    def __init__(self, record_seconds=20):
        gevent.Greenlet.__init__(self)
        self.record_seconds = record_seconds

        (self.queue, self.command) = JoinableQueue(), JoinableQueue()

        PA = pyaudio.PyAudio()
        self.pa = PA.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

    def _run(self):
        print 'mic_on'
        self.command.put('\0')
        start = time.time()
        while True:
            try:
                frame = self.pa.read(self.CHUNK)
            except IOError:
                frame = '\0'
            self.queue.put(frame)
            time.sleep(0.00001)
            if time.time() -  start > self.record_seconds:
                print 'timed mic'
                self.exit()
                self.command.task_done()
                break

    def exit(self):
        print 'stopping'
        self.pa.close()


if __name__ == '__main__':
    _mic = Microphone(record_seconds=10)
    _trn = Transmitter(_mic)
    _mic.start()
    _trn.start()
    print 'start'
    time.sleep(1)
    _mic.command.join()
    print 'end'
