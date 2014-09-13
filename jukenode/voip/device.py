import time, sys
from gevent import monkey; monkey.patch_all()
import gevent
from gevent.queue import Queue, Empty

import socket
import pyaudio


class __AudioNode(gevent.Greenlet):
    RATE = 44100
    CHUNK = 512
    PORT = 20000

    def __init__(self, is_log=True):
        gevent.Greenlet.__init__(self)
        self.is_log = is_log
        self.command = Queue()

    def is_quit(self):
        try:
            cmd = self.command.get_nowait()
            return cmd == 'q'
        except Empty:
            return False

    def stop(self, msg=''):
        self.command.put('q')
        if self.is_log:
            print '%s - stopping %s' % (self.__class__.__name__, msg)

    def _run(self):
        if self.is_log:  print 'starting: %s' % self.__class__.__name__
        try:
            self.engine()
        finally:
            self.pa.close()
            self.sock.close()



class Microphone(__AudioNode):
    def __init__(self, dest, record_seconds=20):
        super(self.__class__, self).__init__()

        self.record_seconds = record_seconds
        PA = pyaudio.PyAudio()
        self.pa = PA.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
##            speaker_ip = socket.gethostbyname(dest)
            self.trn_addr = (dest, self.PORT)
            if self.is_log:  print 'mic_init'
        except Exception as e:
            print("couldn't find :%s" % dest)
            self.stop('speaker_not_found_error')


    def engine(self):
        if self.is_log:  print('mic_engine')
        start_time = time.time()
        for i in range(11):
            try:
                self.sock.connect(self.trn_addr)
                if self.is_log:  print ('connected to speaker: {0}'.format(self.trn_addr[0]))
                break
            except socket.error as e:
                print e
                print('%s. looking for speaker-out on :%s' % (i+1, self.trn_addr))
                time.sleep(3)
        else:
            print 'Could not find speaker'
            self.stop()
            return

        while True:
            try:
                time.sleep(0.0001)
                frame = self.pa.read(self.CHUNK)
                self.sock.send(frame)
            except IOError:
                pass

            if self.is_quit():
                break
            elif time.time() -  start_time > self.record_seconds:
                self.stop('time-out')



class Speaker(__AudioNode):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(
            ('', self.PORT)
        )
        PA = pyaudio.PyAudio()
        self.pa= PA.open(
            format= pyaudio.paInt16,
            channels= 1,
            rate= self.RATE,
            output= True
        )
        print 'speaker init'

    def engine(self):
        self.sock.listen(30)
        (clientsocket, address) = self.sock.accept()
        if self.is_log:  print 'Microphone connected from: %s' % address[0]

        while True:
            time.sleep(0.0001)
            try:
                frame = clientsocket.recv(self.CHUNK)
                if not frame:
                    self.stop('network break')
##                sys.stdout.write('/') ; sys.stdout.flush()
            except network.Empty:
                frame = '\0'
            self.pa.write(frame)

            if self.is_quit():
                break

        clientsocket.close()
