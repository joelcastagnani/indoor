from datetime import datetime
from pathlib import Path
import time
import serial

puerto = "/dev/ttyUSB0"
salida = Path("datos/logs/sensor.csv")
pausa = Path("datos/puerto.pedir")
rele1 = Path("datos/rele.txt")
rele2 = Path("datos/rele2.txt")

def bit(path):
    if not path.exists():
        return 0
    return 1 if path.read_text().strip() == "on" else 0

def orden():
    return f"R {bit(rele1)} {bit(rele2)}\n"

print("logueando. Ctrl+C para salir.")
ser = None
ultima = None
while True:
    if pausa.exists():
        if ser is not None:
            ser.close()
            ser = None
        time.sleep(0.2)
        continue
    if ser is None:
        ser = serial.Serial()
        ser.port = puerto
        ser.baudrate = 115200
        ser.timeout = 3
        ser.dtr = False
        ser.rts = False
        ser.open()
        ser.dtr = False
        ser.rts = False
        time.sleep(2)
        ser.reset_input_buffer()
        ultima = None
    ahora_orden = orden()
    if ahora_orden != ultima:
        ser.write(ahora_orden.encode())
        ultima = ahora_orden
    linea = ser.readline().decode("utf-8", errors="ignore").strip()
    if linea and "," in linea and "rst:" not in linea and not linea.startswith("R "):
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fila = f"{ahora},{linea}"
        print(fila)
        with salida.open("a") as f:
            f.write(fila + "\n")