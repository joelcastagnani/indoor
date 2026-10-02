import subprocess
from datetime import datetime
from pathlib import Path
from time import sleep

dispositivo = "/dev/video0"
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

def fijar_exposicion():
    subprocess.run(
        ["v4l2-ctl", "-d", dispositivo, "--set-ctrl=auto_exposure=1"],
        check=False,
    )
    subprocess.run(
        ["v4l2-ctl", "-d", dispositivo, "--set-ctrl=exposure_time_absolute=10"],
        check=False,
    )

while True:
    if en_luz() and grabar_activado():
        print("GRABANDO 10 min + preview", datetime.now().strftime("%H:%M:%S"))
        nombre = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
        comando = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "v4l2", "-input_format", "mjpeg",
            "-video_size", "1280x720", "-framerate", "15",
            "-t", "600",
            "-i", dispositivo,
            "-c:v", "copy",
            "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
            str(carpeta / nombre),
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
    fijar_exposicion()
    subprocess.run(comando)
