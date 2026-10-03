import time
from datetime import datetime
import subprocess
from pathlib import Path

carpeta = Path("datos/fotos")
intervalo = 30  # segundos; más adelante lo cambiamos

def camara_c920():
    salida = subprocess.run(
        ["v4l2-ctl", "--list-devices"],
        capture_output=True, text=True, check=True,
    ).stdout
    en_c920 = False
    for linea in salida.splitlines():
        if "HD Pro Webcam C920" in linea:
            en_c920 = True
            continue
        if en_c920 and linea.startswith("\t/dev/video"):
            return linea.strip()
        if en_c920 and linea and not linea.startswith("\t"):
            break
    raise RuntimeError("no encontré la C920")

print("loop de fotos. Ctrl+C para salir.")
while True:
    camara = camara_c920()
    nombre = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
    destino = carpeta / nombre
    subprocess.run(
        ["v4l2-ctl", "-d", camara,
         "--set-ctrl=auto_exposure=1",
         "--set-ctrl=exposure_time_absolute=10",
         "--set-ctrl=gain=0"],
        check=False,
    )
    comando = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-f", "v4l2",
        "-video_size", "1280x720",
        "-i", camara,
        "-frames:v", "1",
        str(destino),
    ]
    subprocess.run(comando, check=True)
    print(f"guardada: {destino} ({camara})")
    time.sleep(intervalo)