#   Extract basic header information from a WAV file
import os, sys
import struct

def header_report(wav_file_name):
    EOF = 2
    chunk_name = lambda _: _[0:4].decode()

    with open(wav_file_name, 'rb') as in_file:
        wav_hdr = in_file.read(38)
        unpack = lambda fmt, x, y: struct.unpack(fmt, wav_hdr[x:y])[0]

        if chunk_name(wav_hdr) != "RIFF" or wav_hdr[12:16] != b"fmt ":
            raise Exception("Bad WAV: %s, hdr: %s, fmt: %s" % (wav_file_name, chunk_name(wav_hdr), wav_hdr[12:16]))

        in_file.seek(0, EOF)
        file_size = in_file.tell()

        yield "Chunks: "
        nxt_chunk_loc = 12
        while nxt_chunk_loc < file_size:
            in_file.seek(nxt_chunk_loc)
            chunk_h = in_file.read(8)
            chunk_size = struct.unpack('<L', chunk_h[4:8])[0]
            if chunk_name(chunk_h) == 'data':
                yield "\t%s, offset: %s, size: %sk" % (chunk_name(chunk_h), nxt_chunk_loc, chunk_size // 1024)
            nxt_chunk_loc += 8 + chunk_size

        for (key, data) in {
            'Audio size': str(unpack('<L', 4, 8) // 1024)+"k",
            'Format' : wav_hdr[8:12].decode(),
            'Subchunk1Size': unpack('<L', 16, 20),
            'Audio format': unpack('<H', 20, 22),
            'Channels': unpack('<H', 22, 24),
            'Sample rate': str(unpack('<L', 24, 28) // 1000) + 'k',
            'Byte rate': str(unpack('<L', 28, 32) // 1000) +'k',
            'Block align': unpack('<H', 32, 34),
            'Bits per sample': unpack('<H', 34, 36),
        }.items():
            yield "%s: %s" % (key, data)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("WAVE path missing!")
        sys.exit(1)

    for rec in header_report(sys.argv[1]):
        print(rec)