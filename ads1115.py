import time
import struct


class ADS1115:
    # PGA full scale ranges in volts, index = config bits
    _FSR = (6.144, 4.096, 2.048, 1.024, 0.512, 0.256)

    def __init__(self, i2c, addr=0x48, pga=1, dr=7):
        self.i2c = i2c
        self.addr = addr
        self.pga = pga
        self.dr = dr  # 7 = 860 SPS
        self.lsb = self._FSR[pga] / 32768

    def read_raw(self, ch):
        """Single-shot single-ended conversion on AIN<ch>."""
        cfg = (0x8000 | ((4 + ch) << 12) | (self.pga << 9)
               | (1 << 8) | (self.dr << 5) | 0x03)
        self.i2c.writeto_mem(self.addr, 1, struct.pack(">H", cfg))
        for _ in range(100):
            if struct.unpack(">H", self.i2c.readfrom_mem(self.addr, 1, 2))[0] & 0x8000:
                break
            time.sleep_us(100)
        return struct.unpack(">h", self.i2c.readfrom_mem(self.addr, 0, 2))[0]

    def read_voltage(self, ch):
        return self.read_raw(ch) * self.lsb
