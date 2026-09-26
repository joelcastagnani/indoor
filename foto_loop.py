import time
from datetime import datetime
import subprocess
from pathlib import Path

carpeta = Path("datos/fotos")
intervalo = 30  # segundos; más adelante lo cambiamos

print("loop de fotos. Ctrl+C para salir.")

while True:
    nombre = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
    destino = carpeta / nombre
    comando = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-f", "v4l2",
        "-video_size", "1280x720",
        "-i", "/dev/video2",
        "-frames:v", "1",
        str(destino),
    ]
    subprocess.run(comando, check=True)
    print(f"guardada: {destino}")
    time.sleep(intervalo)
