from machine import Pin, SoftI2C
from time import sleep_ms, sleep

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
addr = 0x38
i2c.writeto(addr, bytes([0xBE, 0x08, 0x00]))
sleep_ms(20)

def leer():
    i2c.writeto(addr, bytes([0xAC, 0x33, 0x00]))
    sleep_ms(80)
    d = i2c.readfrom(addr, 6)
    raw_h = ((d[1] << 16) | (d[2] << 8) | d[3]) >> 4
    raw_t = ((d[3] & 0x0F) << 16) | (d[4] << 8) | d[5]
    h = raw_h * 100 / 1048576
    t = raw_t * 200 / 1048576 - 50
    return round(t, 2), round(h, 1)

while True:
    try:
        t, h = leer()
        print(f"{t}, {h}")
    except:
        pass
    sleep(2)
