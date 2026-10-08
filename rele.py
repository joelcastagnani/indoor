from machine import Pin

def _pedido():
    try:
        f = open("rele_estado.txt")
        a, b = f.read().split()
        f.close()
        return int(a), int(b)
    except:
        return 0, 0

def _pin(n, prendido):
    return Pin(n, Pin.OUT, value=0 if prendido else 1)

a0, b0 = _pedido()
rele = _pin(23, a0)
rele2 = _pin(18, b0)

def aplicar(a, b):
    rele.value(0 if a else 1)
    rele2.value(0 if b else 1)
    f = open("rele_estado.txt", "w")
    f.write("%d %d\n" % (a, b))
    f.close()
    print("aplicar", a, b)