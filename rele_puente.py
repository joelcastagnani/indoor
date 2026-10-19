import time
from pathlib import Path
import serial

PUERTO = "/dev/ttyUSB0"
ARCHIVO = Path("/tmp/rele_cmd")

ser = serial.Serial(PUERTO, 115200, timeout=0.1)
print("puente de reles listo")

while True:
    if ARCHIVO.exists():
        try:
            texto = ARCHIVO.read_text().strip()
            ARCHIVO.unlink()
            partes = texto.split()
            if len(partes) == 5 and partes[0] == "R":
                linea = texto + "\n"
                ser.write(linea.encode())
                print("mando:", texto)
        except Exception as e:
            print("error:", e)
    time.sleep(0.05)