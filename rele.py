from machine import Pin

rele = Pin(23, Pin.OUT, value=1)

def on():
    rele.value(0)
    print("prendido")

def off():
    rele.value(1)
    print("apagado")
