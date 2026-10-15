from datetime import datetime
from pathlib import Path
import termios
import time
import serial

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

def medicion(linea):
    partes = linea.split(",")
    if len(partes) != 2:
        return False
    try:
        float(partes[0].strip())
        float(partes[1].strip())
        return True
    except ValueError:
        return False

def sin_corte(ser):
    attrs = termios.tcgetattr(ser.fileno())
    attrs[2] = attrs[2] & ~termios.HUPCL
    termios.tcsetattr(ser.fileno(), termios.TCSANOW, attrs)
    ser.dtr = False
    ser.rts = False

def puerto_esp32():
    for p in Path("/dev").glob("ttyUSB*"):
        if p.exists():
            return str(p)
    return None

print("logueando. Ctrl+C para salir.")
ser = None
ultima = None
ultima_fila = None

while True:
    if pausa.exists():
        if ser is not None:
            ser.close()
            ser = None
        time.sleep(0.2)
        continue

    if ser is None:
        puerto = puerto_esp32()
        if not puerto:
            print("esperando ESP32...", datetime.now().strftime("%H:%M:%S"))
            time.sleep(5)
            continue
        try:
            ser = serial.Serial()
            ser.port = puerto
            ser.baudrate = 115200
            ser.timeout = 0.2
            ser.dsrdtr = False
            ser.rtscts = False
            ser.dtr = False
            ser.rts = False
            ser.open()
            time.sleep(0.1)
            ser.dtr = False
            ser.rts = False
            sin_corte(ser)
            time.sleep(3)
            ser.reset_input_buffer()
            ser.timeout = 3
            ultima = None
            print("conectado a", puerto)
        except Exception as e:
            print("no pude abrir", puerto, e)
            ser = None
            time.sleep(5)
            continue

    try:
        ahora_orden = orden()
        if ahora_orden != ultima:
            ser.write(ahora_orden.encode())
            ultima = ahora_orden
        linea = ser.readline().decode("utf-8", errors="ignore").strip()
        if not medicion(linea):
            continue
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fila = f"{ahora},{linea}"
        if fila == ultima_fila:
            continue
        ultima_fila = fila
        print(fila)
        with salida.open("a") as f:
            f.write(fila + "\n")
    except Exception as e:
        print("error sensor:", e)
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass
            ser = None
        time.sleep(3)