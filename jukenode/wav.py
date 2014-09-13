#https://ccrma.stanford.edu/courses/422/projects/WaveFormat/
import _io, struct
import pyaudio


class Wav(object):
    def __init__(self, filename):
        self.filename = filename
        with _io.open(filename, 'rb') as wav:
            self.__raw_header = wav.read(72)
            self.__struct_header = struct.unpack('4sL4s4sLHHLLHH4sL', self.__raw_header)
            self.chunk_id, \
                self.chunk_size, \
                self.format, \
                self.sub_chunk_id_1, \
                self.sub_chunk_size_1, \
                self.format, \
                self.num_channel, \
                self.sample_rate_bit, \
                self.byte_rate, \
                self.block_align, \
                self.bit_per_sample, \
                self.sub_chunk_id_2, \
                self.sub_chunk_size_2 = self.__struct_header
            self.is_compressed = False if self.format == 1 else True
            self.byte_per_sample = int(self.bit_per_sample / 8)
            self.data = wav.read()
        self.len = len(self.data)
        self.__struct_mask = {1:'B',2:'H',4:'I',8:'Q'}[self.byte_per_sample]
        self.__struct_mask = self.__struct_mask * self.num_channel
        self.__sample_bytes = self.byte_per_sample * self.num_channel

    def __enter__(self):
        self.pa = pyaudio.PyAudio().open(
            format= pyaudio.paInt8,
            channels = self.num_channel,
            rate= self.sample_rate_bit,
            output= True
        )
        return self

    def __exit__(self , type, value, traceback):
        self.pa.close()
        if  traceback:
            print(traceback)

    def __iter__(self):
        p=-1
        while p < (len(self)/self.__sample_bytes)-self.__sample_bytes:
            p += 1
            chunk = self.data[p * self.block_align:(p * self.block_align) + self.block_align]
            yield struct.unpack(self.__struct_mask, chunk)
        else:
            raise StopIteration

    def __len__(self):
        return int(len(self.data)/self.block_align)

    def __getitem__(self, key):
        if type(key) != int: raise TypeError
        if key > len(self): raise KeyError
        chunk = self.data[key * self.block_align:(key * self.block_align) + self.block_align]
        return struct.unpack(self.__struct_mask, chunk)

    def play(self):
        for chunk in self:
            self.pa.write(chunk)

w8 = Wav('tests/sound1.wav')
#pyb.DAC(1).write_timed(w8.data,w8.sample_rate_bit,mode=pyb.DAC.NORMAL)
