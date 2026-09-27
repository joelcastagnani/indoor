from datetime import datetime
from pathlib import Path
import serial

puerto = "/dev/ttyUSB0"
salida = Path("datos/logs/sensor.csv")

print("logueando. Ctrl+C para salir.")

with serial.Serial(puerto, 115200, timeout=2) as ser:
    ser.reset_input_buffer()
    while True:
        linea = ser.readline().decode("utf-8", errors="ignore").strip()
        if not linea or "," not in linea:
            continue
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fila = f"{ahora},{linea}"
        print(fila)
        with salida.open("a") as f:
            f.write(fila + "\n")
