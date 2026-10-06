import subprocess
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, redirect, url_for, send_from_directory, render_template, jsonify
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
    est_sen = "ON" if vivo(sen) else "OFF"
    est_vid = "ON" if grabacion_on() else "OFF"
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clima = parse_clima()
    preview = FOTOS / "preview.jpg"
    preview_v = int(preview.stat().st_mtime) if preview.exists() else None
    return render_template(
        "index.html",
        est_sen=est_sen,
        est_vid=est_vid,
        ahora=ahora,
        clima=clima,
        preview_v=preview_v,
    )


@app.get("/foto/<nombre>")
def servir_foto(nombre):
    return send_from_directory(FOTOS, nombre)

@app.get("/estado")
def estado():
    clima = parse_clima()
    preview = FOTOS / "preview.jpg"
    return jsonify(
        ahora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        temp=clima["temp"] if clima else None,
        hum=clima["hum"] if clima else None,
        preview_v=int(preview.stat().st_mtime) if preview.exists() else None,
    )

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


@app.post("/rele/on")
def rele_on():
    subprocess.run(
        ["/home/rideparkcity1/proyectos/indoor/.venv/bin/mpremote", "connect", "/dev/ttyUSB0", "exec", "import rele; rele.on()"],
        cwd=ROOT,
        timeout=8,
    )
    return redirect(url_for("index"))


@app.post("/rele/off")
def rele_off():
    subprocess.run(
        ["/home/rideparkcity1/proyectos/indoor/.venv/bin/mpremote", "connect", "/dev/ttyUSB0", "exec", "import rele; rele.off()"],
        cwd=ROOT,
        timeout=8,
    )
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(host="0.0.0.0", port=5000, debug=False)
