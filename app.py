import subprocess
import sys
from datetime import datetime
from pathlib import Path
import time

from flask import Flask, redirect, url_for, send_from_directory, render_template, jsonify
app = Flask(__name__)

ROOT = Path(__file__).resolve().parent
FOTOS = ROOT / "datos" / "fotos"
LOG = ROOT / "datos" / "logs" / "sensor.csv"
BANDERA = ROOT / "datos" / "grabar.txt"
BANDERA_RELE = ROOT / "datos" / "rele.txt"
BANDERA_RELE2 = ROOT / "datos" / "rele2.txt"
sen = None


def vivo(p):
    return p is not None and p.poll() is None


def grabacion_on():
    if not BANDERA.exists():
        return False
    return BANDERA.read_text().strip().lower() == "on"


def rele_prendido():
    if not BANDERA_RELE.exists():
        return False
    return BANDERA_RELE.read_text().strip().lower() == "on"

def rele2_prendido():
    if not BANDERA_RELE2.exists():
        return False
    return BANDERA_RELE2.read_text().strip().lower() == "on"

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
    est_rele = "ON" if rele_prendido() else "OFF"
    est_rele2 = "ON" if rele2_prendido() else "OFF"
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clima = parse_clima()
    preview = FOTOS / "preview.jpg"
    preview_v = int(preview.stat().st_mtime) if preview.exists() else None
    return render_template(
        "index.html",
        est_sen=est_sen,
        est_vid=est_vid,
        est_rele=est_rele,
        est_rele2=est_rele2,
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


def aplicar_reles():
    a = 1 if rele_prendido() else 0
    b = 1 if rele2_prendido() else 0
    pausa = ROOT / "datos" / "puerto.pedir"
    pausa.write_text("1\n")
    time.sleep(2)
    for _ in range(25):
        r = subprocess.run(["fuser", "/dev/ttyUSB0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
            break
        time.sleep(0.2)
    try:
        subprocess.run(
            # hola
            ["/home/rideparkcity1/proyectos/indoor/.venv/bin/mpremote", "connect", "/dev/ttyUSB0", "resume", "exec",
             "import rele; rele.aplicar(%d, %d)" % (a, b)],
            # hola
            cwd=ROOT,
            timeout=12,
        )
    finally:
        pausa.unlink(missing_ok=True)

@app.post("/rele/on")
def rele_on():
    BANDERA_RELE.write_text("on\n")
    return redirect(url_for("index"))

@app.post("/rele/off")
def rele_off():
    BANDERA_RELE.write_text("off\n")
    return redirect(url_for("index"))

@app.post("/rele2/on")
def rele2_on():
    BANDERA_RELE2.write_text("on\n")
    return redirect(url_for("index"))

@app.post("/rele2/off")
def rele2_off():
    BANDERA_RELE2.write_text("off\n")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(host="0.0.0.0", port=5000, debug=False)