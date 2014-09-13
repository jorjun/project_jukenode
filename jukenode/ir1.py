import pyb


class IR(object):
    def __init__(self, in_pin, buf_width=72):
        self.in_pin = in_pin
        self.buf_width = buf_width
        self.buf = []
        #self.micros = pyb.Timer(2, prescaler=83, period=50)

    def time_it(self, idx):
        sig = self.in_pin.value()
        while self.in_pin.value() == sig:
            self.buf[idx] += 1
            pyb.udelay(20)
            if  self.buf[idx] > 350:  # EOF
                raise Exception()

    def scan(self):
        idx = 0
        self.buf = [0] * (self.buf_width + 1)
        while idx < self.buf_width:
            try:
                self.time_it(idx)
                idx += 1
            except Exception as exc:
                break

    def main(self):
        while True:
            if not self.in_pin.value():
                self.scan()
                print()
                print(self.buf)
                print("".join(["X" if _ > 29 else " " for _ in self.buf]))
                print()
                pyb.delay(90)
            pyb.udelay(50)

ir = IR(in_pin=pyb.Pin.board.X22)
ir.main()
