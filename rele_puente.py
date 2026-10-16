import time
from pathlib import Path
import serial

PUERTO = "/dev/ttyUSB0"
ARCHIVO = Path("/tmp/rele_cmd")

# Estado actual de los 4 canales (0=apagado, 1=prendido)
estado = [0, 0, 0, 0]

ser = serial.Serial(PUERTO, 115200, timeout=0.1)
print("puente de reles listo")

def mandar():
    linea = f"R {estado[0]} {estado[1]} {estado[2]} {estado[3]}\n"
    ser.write(linea.encode())
    print("mando:", linea.strip())

while True:
    if ARCHIVO.exists():
        try:
            texto = ARCHIVO.read_text().strip()
            ARCHIVO.unlink()
            partes = texto.split()
            if len(partes) >= 3 and partes[0] == "R":
                canal = int(partes[1])
                valor = int(partes[2])
                if 1 <= canal <= 4:
                    estado[canal - 1] = 1 if valor else 0
                    mandar()
        except Exception as e:
            print("error:", e)
    time.sleep(0.05)