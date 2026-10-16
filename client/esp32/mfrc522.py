"""RC522 over SPI. Register addresses are the NXP MFRC522 numbers.

This module talks to the chip only. Card ids, attack/defense, and UDP
live in zone.py and main.py.
"""

from machine import Pin
import time


class MFRC522:
    """RC522 over SPI. Register addresses are the NXP MFRC522 numbers."""

    OK = 0
    NOTAG = 1
    ERR = 2

    def __init__(self, spi, cs, rst):
        """Hold CS and reset idle-high, then run init()."""
        self.spi = spi
        self.cs = cs
        self.rst = rst
        self.cs.init(Pin.OUT, value=1)
        self.rst.init(Pin.OUT, value=1)
        self.init()

    def _wreg(self, reg, val):
        """Write one register. The address is shifted left by 1, per the SPI frame."""
        self.cs.value(0)
        self.spi.write(bytearray([(reg << 1) & 0x7E, val & 0xFF]))
        self.cs.value(1)

    def _rreg(self, reg):
        """Read one register. The address bit 7 marks a read."""
        buf = bytearray([((reg << 1) & 0x7E) | 0x80, 0])
        self.cs.value(0)
        self.spi.write_readinto(buf, buf)
        self.cs.value(1)
        return buf[1]

    def _set(self, reg, mask):
        """Set the bits in mask, leaving the other bits of reg unchanged."""
        self._wreg(reg, self._rreg(reg) | mask)

    def _clear(self, reg, mask):
        """Clear the bits in mask, leaving the other bits of reg unchanged."""
        self._wreg(reg, self._rreg(reg) & ~mask)

    def init(self):
        """Soft-reset the chip, load the timer, and turn the antenna on."""
        self.rst.value(1)
        self._wreg(0x01, 0x0F)
        time.sleep_ms(50)
        self._wreg(0x2A, 0x8D)
        self._wreg(0x2B, 0x3E)
        self._wreg(0x2D, 30)
        self._wreg(0x2C, 0)
        self._wreg(0x15, 0x40)
        self._wreg(0x11, 0x3D)
        self._set(0x14, 0x03)

    def version(self):
        """VersionReg. 0x91 or 0x92 is a real chip; 0x00 and 0xFF mean it is not answering."""
        return self._rreg(0x37)

    def _to_card(self, cmd, send):
        """Run cmd with send. Return (status, received bytes, valid bit count).

        cmd 0x0C is Transceive and 0x0E is MFAuthent. Status is OK, NOTAG, or ERR.
        """
        recv = []
        bits = 0
        irq_en = 0x12 if cmd == 0x0E else 0x77
        wait_irq = 0x10 if cmd == 0x0E else 0x30
        self._wreg(0x02, irq_en | 0x80)
        self._clear(0x04, 0x80)
        self._set(0x0A, 0x80)
        self._wreg(0x01, 0x00)
        for byte in send:
            self._wreg(0x09, byte)
        self._wreg(0x01, cmd)
        if cmd == 0x0C:
            self._set(0x0D, 0x80)
        irq = 0
        for _ in range(2000):
            irq = self._rreg(0x04)
            if irq & 0x01 or irq & wait_irq:
                break
        else:
            self._clear(0x0D, 0x80)
            return self.ERR, recv, bits
        self._clear(0x0D, 0x80)
        if self._rreg(0x06) & 0x1B:
            return self.ERR, recv, bits
        if irq & irq_en & 0x01:
            return self.NOTAG, recv, bits
        if cmd == 0x0C:
            count = self._rreg(0x0A)
            last = self._rreg(0x0C) & 0x07
            if last:
                bits = (count - 1) * 8 + last
            else:
                bits = count * 8
            if count == 0:
                count = 1
            if count > 16:
                count = 16
            for _ in range(count):
                recv.append(self._rreg(0x09))
        return self.OK, recv, bits

    def _crc(self, data):
        """ISO CRC of data, low byte first, computed by the chip."""
        self._clear(0x05, 0x04)
        self._set(0x0A, 0x80)
        for byte in data:
            self._wreg(0x09, byte)
        self._wreg(0x01, 0x03)
        for _ in range(255):
            if self._rreg(0x05) & 0x04:
                break
        return [self._rreg(0x22), self._rreg(0x21)]

    def request(self):
        """REQA. OK when a tag answers with a 16-bit ATQA."""
        self._wreg(0x0D, 0x07)
        stat, _recv, bits = self._to_card(0x0C, [0x26])
        if stat != self.OK or bits != 0x10:
            return self.ERR
        return self.OK

    def anticoll(self):
        """Anticollision for cascade level 1. Return (OK, 5-byte uid) or (ERR, None)."""
        self._wreg(0x0D, 0x00)
        stat, recv, _bits = self._to_card(0x0C, [0x93, 0x20])
        if stat != self.OK or len(recv) != 5:
            return self.ERR, None
        checksum = 0
        for byte in recv[:4]:
            checksum ^= byte
        if checksum != recv[4]:
            return self.ERR, None
        return self.OK, recv

    def select(self, uid):
        """SELECT the 5-byte uid. OK when the tag returns a 24-bit SAK."""
        buf = [0x93, 0x70] + list(uid[:5])
        buf += self._crc(buf)
        stat, _recv, bits = self._to_card(0x0C, buf)
        if stat == self.OK and bits == 0x18:
            return self.OK
        return self.ERR

    def auth(self, block, key, uid):
        """Authenticate block with key A. uid is the first four uid bytes. Return status."""
        payload = [0x60, block] + list(key) + list(uid[:4])
        return self._to_card(0x0E, payload)[0]

    def stop_crypto(self):
        """Clear MFCrypto1On so the next tag starts unauthenticated."""
        self._clear(0x08, 0x08)

    def read_block(self, block):
        """16 bytes of an authenticated block, or None on failure."""
        data = [0x30, block]
        data += self._crc(data)
        stat, recv, _bits = self._to_card(0x0C, data)
        if stat != self.OK or len(recv) < 16:
            return None
        return recv[:16]
