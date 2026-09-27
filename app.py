import subprocess
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, redirect, url_for, send_from_directory

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent
FOTOS = ROOT / "datos" / "fotos"
LOG = ROOT / "datos" / "logs" / "sensor.csv"
BANDERA = ROOT / "datos" / "grabar.txt"
sen = None


def vivo(p):
    return p is not None and p.poll() is None


def grabacion_on():
    if not BANDERA.exists():
        return False
    return BANDERA.read_text().strip().lower() == "on"


def parse_clima():
    if not LOG.exists():
        return None
    lineas = LOG.read_text().strip().splitlines()
    if not lineas:
        return None
    partes = [p.strip() for p in lineas[-1].split(",")]
    if len(partes) < 3:
        return None
    return {"temp": partes[1], "hum": partes[2]}


@app.get("/")
def index():
    est_sen = "prendido" if vivo(sen) else "apagado"
    est_vid = "ON" if grabacion_on() else "OFF"
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clima = parse_clima()
    if clima:
        bloque_clima = (
            f"<p>Temperatura: <strong>{clima['temp']} °C</strong></p>"
            f"<p>Humedad: <strong>{clima['hum']} %</strong></p>"
        )
    else:
        bloque_clima = "<p>Temperatura: —</p><p>Humedad: —</p>"
    preview = FOTOS / "preview.jpg"
    if preview.exists():
        bloque_foto = (
            f'<img src="/foto/preview.jpg?v={int(preview.stat().st_mtime)}" '
            f'alt="vivo" '
            f'style="width:100%;max-width:28rem;height:auto;display:block;">'
        )
    else:
        bloque_foto = "<p>Sin imagen</p>"
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="2">
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
    {bloque_foto}
  </section>
  <section>
    <p>Fecha y hora: <strong>{ahora}</strong></p>
    {bloque_clima}
  </section>
  <section>
    <p>Grabación: <strong>{est_vid}</strong></p>
    <form method="post" action="/vid/on"><button type="submit">Grabar ON</button></form>
    <form method="post" action="/vid/off"><button type="submit">Grabar OFF</button></form>
  </section>
  <section>
    <p>Sensor: <strong>{est_sen}</strong></p>
    <form method="post" action="/sen/on"><button type="submit">Iniciar sensor</button></form>
    <form method="post" action="/sen/off"><button type="submit">Detener sensor</button></form>
  </section>
</body>
</html>
"""


@app.get("/foto/<nombre>")
def servir_foto(nombre):
    return send_from_directory(FOTOS, nombre)


@app.post("/vid/on")
def vid_on():
    BANDERA.write_text("on\n")
    return redirect(url_for("index"))


@app.post("/vid/off")
def vid_off():
    BANDERA.write_text("off\n")
    return redirect(url_for("index"))


@app.post("/sen/on")
def sen_on():
    global sen
    if not vivo(sen):
        sen = subprocess.Popen(
            [sys.executable, str(ROOT / "log_sensor.py")],
            cwd=ROOT,
        )
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
