import subprocess
from datetime import datetime
from pathlib import Path
from time import sleep

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
    return h >= 18 or h < 12

def grabar_activado():
    if not bandera.exists():
        return False
    return bandera.read_text().strip().lower() == "on"

def fijar_exposicion(dispositivo):
    subprocess.run(
        ["v4l2-ctl", "-d", dispositivo,
         "--set-ctrl=auto_exposure=1",
         "--set-ctrl=exposure_time_absolute=10",
         "--set-ctrl=gain=0"],
        check=False,
    )

print("preview 24h; mp4 si grabar=on y 18:00-12:00. Ctrl+C para salir.")
while True:
    try:
        dispositivo = camara_c920()
    except Exception:
        print("esperando C920...", datetime.now().strftime("%H:%M:%S"))
        sleep(5)
        continue

    if en_luz() and grabar_activado():
        print("GRABANDO 1 h + preview", datetime.now().strftime("%H:%M:%S"), dispositivo)
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
    try:
        fijar_exposicion(dispositivo)
        subprocess.run(comando, timeout=3700)
    except Exception as e:
        print("error video:", e)
    sleep(2)