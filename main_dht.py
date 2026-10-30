import machine
import dht
import time

sensor = dht.DHT22(machine.Pin(4))

while True:
    try:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        print(round(t, 2), ",", round(h, 1))
    except:
        print("error")
    time.sleep(2)
