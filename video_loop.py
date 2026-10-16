import subprocess
from datetime import datetime
from pathlib import Path
from time import sleep
import config

preview = Path("datos/fotos/preview.jpg")
carpeta = Path("datos/video")
bandera = Path("datos/grabar.txt")

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

def en_luz(ahora=None):
    ahora = ahora or datetime.now()
    h = ahora.hour
    return h >= config.HORA_LUZ_INICIO or h < config.HORA_LUZ_FIN

def grabar_activado():
    if not bandera.exists():
        return False
    return bandera.read_text().strip().lower() == "on"

def fijar_exposicion(dispositivo):
    subprocess.run(
        ["v4l2-ctl", "-d", dispositivo,
         "--set-ctrl=auto_exposure=1",
         "--set-ctrl=exposure_time_absolute=" + str(config.EXPOSURE_TIME),
         "--set-ctrl=gain=" + str(config.GAIN)],
        check=False,
    )

print("preview 24h; mp4 si grabar=on y 18:00-12:00. Ctrl+C para salir.")
while True:
    dispositivo = camara_c920()
    if en_luz() and grabar_activado():
        print("GRABANDO 10 min + preview", datetime.now().strftime("%H:%M:%S"), dispositivo)
        nombre = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
        comando = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "v4l2", "-input_format", "mjpeg",
            "-video_size", "1280x720", "-framerate", "15",
            "-t", "3600",
            "-i", dispositivo,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
            "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
            str(carpeta / nombre),
            "-vf", "fps=1", "-update", "1", str(preview),
        ]
    else:
        print("solo preview", datetime.now().strftime("%H:%M:%S"), dispositivo)
        comando = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "v4l2", "-input_format", "mjpeg",
            "-video_size", "1280x720", "-framerate", "15",
            "-i", dispositivo,
            "-t", "60",
            "-vf", "fps=1", "-update", "1", str(preview),
        ]
    fijar_exposicion(dispositivo)
    subprocess.run(comando)
    sleep(2)