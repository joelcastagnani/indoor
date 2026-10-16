import serial
import time
from pathlib import Path

puerto = "/dev/ttyUSB0"
log = Path("datos/logs/sensor.csv")
log.parent.mkdir(parents=True, exist_ok=True)

ser = serial.Serial(puerto, 115200, timeout=1)
time.sleep(2)

print("logueando. Ctrl+C para salir.")
while True:
    try:
        with open("/tmp/rele_cmd") as f:
            cmd = f.read().strip()
        if cmd:
            ser.write((cmd + "\n").encode())
            open("/tmp/rele_cmd", "w").close()
    except FileNotFoundError:
        pass

    linea = ser.readline().decode(errors="ignore").strip()
    if linea and "," in linea:
        with open(log, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')},{linea}\n")
    time.sleep(0.1)