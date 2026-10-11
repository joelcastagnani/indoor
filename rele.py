from machine import Pin

def _pedido():
    try:
        f = open("rele_estado.txt")
        partes = f.read().split()
        f.close()
        while len(partes) < 4:
            partes.append("0")
        return [int(x) for x in partes[:4]]
    except:
        return [0, 0, 0, 0]

def _pin(n, prendido):
    return Pin(n, Pin.OUT, value=0 if prendido else 1)

estado0 = _pedido()
reles = [
    _pin(23, estado0[0]),
    _pin(18, estado0[1]),
    _pin(19, estado0[2]),
    _pin(5, estado0[3]),
]

def aplicar(a, b, c, d):
    vals = [a, b, c, d]
    for pin, v in zip(reles, vals):
        pin.value(0 if v else 1)
    f = open("rele_estado.txt", "w")
    f.write("%d %d %d %d\n" % (a, b, c, d))
    f.close()
    print("aplicar", a, b, c, d)