from machine import Pin
rele = Pin(23, Pin.OUT, value=1)
rele2 = Pin(18, Pin.OUT, value=1)
def on():
    rele.value(0)
    print("prendido")
def off():
    rele.value(1)
    print("apagado")
def on2():
    rele2.value(0)
    print("canal 2 prendido")
def off2():
    rele2.value(1)
    print("canal 2 apagado")
def aplicar(a, b):
    rele.value(0 if a else 1)
    rele2.value(0 if b else 1)
    print("aplicar", a, b)