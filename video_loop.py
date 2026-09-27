import subprocess
from datetime import datetime
from pathlib import Path
from time import sleep

dispositivo = "/dev/video2"
preview = Path("datos/fotos/preview.jpg")
carpeta = Path("datos/video")
bandera = Path("datos/grabar.txt")


def en_luz(ahora=None):
    ahora = ahora or datetime.now()
    h = ahora.hour
    return h >= 18 or h < 12


def grabar_activado():
    if not bandera.exists():
        return False
    return bandera.read_text().strip().lower() == "on"


print("preview 24h; mp4 si grabar=on y 18:00-12:00. Ctrl+C para salir.")

while True:
    if en_luz() and grabar_activado():
        print("GRABANDO 10 min + preview", datetime.now().strftime("%H:%M:%S"))
        comando = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "v4l2", "-input_format", "mjpeg",
            "-video_size", "1280x720", "-framerate", "15",
            "-i", dispositivo,
            "-t", "600",
            "-c:v", "copy",
            "-f", "segment", "-segment_time", "600",
            "-reset_timestamps", "1", "-strftime", "1",
            str(carpeta / "%Y-%m-%d_%H-%M-%S.mp4"),
            "-vf", "fps=1", "-update", "1", str(preview),
        ]
    else:
        print("solo preview", datetime.now().strftime("%H:%M:%S"))
        comando = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "v4l2", "-input_format", "mjpeg",
            "-video_size", "1280x720", "-framerate", "15",
            "-i", dispositivo,
            "-t", "60",
            "-vf", "fps=1", "-update", "1", str(preview),
        ]
    subprocess.run(comando)
