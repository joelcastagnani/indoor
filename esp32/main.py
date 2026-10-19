# import sys
# import uselect
# from machine import Pin, SoftI2C
# from time import sleep_ms
# import rele

# i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
# addr = 0x38
# i2c.writeto(addr, bytes([0xBE, 0x08, 0x00]))
# sleep_ms(20)
# poll = uselect.poll()
# poll.register(sys.stdin, uselect.POLLIN)

# def leer_orden():
#     if not poll.poll(0):
#         return
#     linea = sys.stdin.readline().strip()
#     if not linea.startswith("R "):
#         return
#     partes = linea.split()
#     if len(partes) == 5:
#         rele.aplicar(int(partes[1]), int(partes[2]), int(partes[3]), int(partes[4]))

# while True:
#     leer_orden()
#     i2c.writeto(addr, bytes([0xAC, 0x33, 0x00]))
#     sleep_ms(80)
#     d = i2c.readfrom(addr, 6)
#     raw_h = ((d[1] << 16) | (d[2] << 8) | d[3]) >> 4
#     raw_t = ((d[3] & 0x0F) << 16) | (d[4] << 8) | d[5]
#     h = raw_h * 100 / 1048576
#     t = raw_t * 200 / 1048576 - 50
#     print(round(t, 2), ",", round(h, 1))
#     for _ in range(20):
#         leer_orden()
#         sleep_ms(500)


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
<<<<<<< HEAD
    return round(t, 2), round(h, 1)

while True:
    try:
        t, h = leer()
        print(f"{t}, {h}")
    except:
        pass
    sleep(2)
=======
    print(round(t, 2), ",", round(h, 1))
    for _ in range(6):
        leer_orden()
        sleep_ms(500)
>>>>>>> origin/v2
