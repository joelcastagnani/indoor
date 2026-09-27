import subprocess
import sys
from pathlib import Path

from flask import Flask, redirect, url_for

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent
LOG = ROOT / "datos" / "logs" / "sensor.csv"
cam = None
sen = None


def vivo(p):
    return p is not None and p.poll() is None


def ultima_lectura():
    if not LOG.exists():
        return "sin datos todavía"
    lineas = LOG.read_text().strip().splitlines()
    return lineas[-1] if lineas else "sin datos todavía"


@app.get("/")
def index():
    est_cam = "prendida" if vivo(cam) else "apagada"
    est_sen = "prendido" if vivo(sen) else "apagado"
    clima = ultima_lectura()
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="10">
  <title>Indoor</title>
  <style>
    body {{ font-family: sans-serif; max-width: 32rem; margin: 3rem auto; }}
    section {{ margin-bottom: 1.5rem; }}
    form {{ display: inline-block; margin-right: 0.4rem; }}
    button {{ padding: 0.55rem 1rem; font-size: 1rem; }}
  </style>
</head>
<body>
  <h1>Indoor</h1>
  <section>
    <p>Cámara: <strong>{est_cam}</strong></p>
    <form method="post" action="/cam/on"><button type="submit">Iniciar cámara</button></form>
    <form method="post" action="/cam/off"><button type="submit">Detener cámara</button></form>
  </section>
  <section>
    <p>Sensor: <strong>{est_sen}</strong></p>
    <p>Última lectura: <strong>{clima}</strong></p>
    <form method="post" action="/sen/on"><button type="submit">Iniciar sensor</button></form>
    <form method="post" action="/sen/off"><button type="submit">Detener sensor</button></form>
  </section>
</body>
</html>
"""


@app.post("/cam/on")
def cam_on():
    global cam
    if not vivo(cam):
        cam = subprocess.Popen([sys.executable, str(ROOT / "foto_loop.py")], cwd=ROOT)
    return redirect(url_for("index"))


@app.post("/cam/off")
def cam_off():
    global cam
    if vivo(cam):
        cam.terminate()
        try:
            cam.wait(timeout=8)
        except subprocess.TimeoutExpired:
            cam.kill()
    return redirect(url_for("index"))


@app.post("/sen/on")
def sen_on():
    global sen
    if not vivo(sen):
        sen = subprocess.Popen([sys.executable, str(ROOT / "log_sensor.py")], cwd=ROOT)
    return redirect(url_for("index"))


@app.post("/sen/off")
def sen_off():
    global sen
    if vivo(sen):
        sen.terminate()
        try:
            sen.wait(timeout=8)
        except subprocess.TimeoutExpired:
            sen.kill()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
