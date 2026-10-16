import serial
import time
from pathlib import Path

CMD = Path("/tmp/rele_cmd")
puerto = "/dev/ttyUSB0"
baud = 115200

ser = serial.Serial(puerto, baud, timeout=0.1)
print("puente de reles listo")

ultimo = ""
while True:
    if CMD.exists():
        texto = CMD.read_text().strip()
        if texto and texto != ultimo:
            for linea in texto.splitlines():
                if linea.strip():
                    ser.write((linea.strip() + "\n").encode())
                    print("mando:", linea.strip())
            ultimo = texto
    time.sleep(0.3)