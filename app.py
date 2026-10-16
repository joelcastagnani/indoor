import subprocess
import sys
from datetime import datetime
from pathlib import Path
import time
import threading
import config

from flask import Flask, redirect, url_for, send_from_directory, render_template, jsonify
app = Flask(__name__)

ROOT = Path(__file__).resolve().parent
FOTOS = ROOT / "datos" / "fotos"
LOG = ROOT / "datos" / "logs" / "sensor.csv"
BANDERA = ROOT / "datos" / "grabar.txt"
BANDERA_RELE = ROOT / "datos" / "rele.txt"
BANDERA_RELE2 = ROOT / "datos" / "rele2.txt"
BANDERA_RELE3 = ROOT / "datos" / "rele3.txt"
BANDERA_RELE4 = ROOT / "datos" / "rele4.txt"
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


def rele3_prendido():
    if not BANDERA_RELE3.exists():
        return False
    return BANDERA_RELE3.read_text().strip().lower() == "on"


def rele4_prendido():
    if not BANDERA_RELE4.exists():
        return False
    return BANDERA_RELE4.read_text().strip().lower() == "on"


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
    est_rele3 = "ON" if rele3_prendido() else "OFF"
    est_rele4 = "ON" if rele4_prendido() else "OFF"
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
        est_rele3=est_rele3,
        est_rele4=est_rele4,
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
    rele1="ON" if rele_prendido() else "OFF",
    rele2="ON" if rele2_prendido() else "OFF",
    rele3="ON" if rele3_prendido() else "OFF",
    rele4="ON" if rele4_prendido() else "OFF",
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
    ya = subprocess.run(["pgrep", "-f", "log_sensor.py"], stdout=subprocess.DEVNULL)
    if ya.returncode != 0:
        sen = subprocess.Popen(
            [sys.executable, str(ROOT / "log_sensor.py")],
            cwd=ROOT,
        )
    return redirect(url_for("index"))


@app.post("/sen/off")
def sen_off():
    global sen
    subprocess.run(["pkill", "-f", "log_sensor.py"])
    sen = None
    return redirect(url_for("index"))


def aplicar_reles():
    a = 1 if rele_prendido() else 0
    b = 1 if rele2_prendido() else 0
    c = 1 if rele3_prendido() else 0
    d = 1 if rele4_prendido() else 0
    pausa = ROOT / "datos" / "puerto.pedir"
    pausa.write_text("1\n")
    time.sleep(4)
    for _ in range(25):
        r = subprocess.run(["fuser", "/dev/ttyUSB0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
            break
        time.sleep(1)
    try:
        subprocess.run(
            ["/home/rideparkcity1/proyectos/indoor/.venv/bin/mpremote", "connect", "/dev/ttyUSB0", "resume", "exec",
             "import rele; rele.aplicar(%d, %d, %d, %d)" % (a, b, c, d)],
            cwd=ROOT,
            timeout=12,
        )
    finally:
        pausa.unlink(missing_ok=True)

def auto_humedad():
    clima = parse_clima()
    if not clima:
        return
    try:
        h = float(clima["hum"])
        t = float(clima["temp"])
    except:
        return

    cambio = False

    # K2
        # K2
    if h >= config.HUMEDAD_K2 and not rele2_prendido():
        BANDERA_RELE2.write_text("on\n")
        print(f"AUTO K2 ON  hum={h:.1f} >= {config.HUMEDAD_K2}")
        cambio = True
    elif h < config.HUMEDAD_K2 and rele2_prendido():
        BANDERA_RELE2.write_text("off\n")
        print(f"AUTO K2 OFF hum={h:.1f} < {config.HUMEDAD_K2}")
        cambio = True

    # K3
    if h >= config.HUMEDAD_K3 and not rele3_prendido():
        BANDERA_RELE3.write_text("on\n")
        print(f"AUTO K3 ON  hum={h:.1f} >= {config.HUMEDAD_K3}")    
        cambio = True
    elif h < config.HUMEDAD_K3 and rele3_prendido():
        BANDERA_RELE3.write_text("off\n")
        print(f"AUTO K3 OFF hum={h:.1f} < {config.HUMEDAD_K3}")
        cambio = True

    # K4
    if t >= config.TEMP_K4 and not rele4_prendido():
        BANDERA_RELE4.write_text("on\n")
        print(f"AUTO K4 ON  temp={t:.1f} >= {config.TEMP_K4}")
        cambio = True
    elif t < config.TEMP_K4 and rele4_prendido():
        BANDERA_RELE4.write_text("off\n")
        print(f"AUTO K4 OFF temp={t:.1f} < {config.TEMP_K4}")
        cambio = True

    if cambio:
        aplicar_reles()

@app.post("/rele/on")
def rele_on():
    BANDERA_RELE.write_text("on\n")
    aplicar_reles()
    return redirect(url_for("index"))


@app.post("/rele/off")
def rele_off():
    BANDERA_RELE.write_text("off\n")
    aplicar_reles()
    return redirect(url_for("index"))


@app.post("/rele2/on")
def rele2_on():
    BANDERA_RELE2.write_text("on\n")
    aplicar_reles()
    return redirect(url_for("index"))


@app.post("/rele2/off")
def rele2_off():
    BANDERA_RELE2.write_text("off\n")
    aplicar_reles()
    return redirect(url_for("index"))


@app.post("/rele3/on")
def rele3_on():
    BANDERA_RELE3.write_text("on\n")
    aplicar_reles()
    return redirect(url_for("index"))


@app.post("/rele3/off")
def rele3_off():
    BANDERA_RELE3.write_text("off\n")
    aplicar_reles()
    return redirect(url_for("index"))


@app.post("/rele4/on")
def rele4_on():
    BANDERA_RELE4.write_text("on\n")
    aplicar_reles()
    return redirect(url_for("index"))


@app.post("/rele4/off")
def rele4_off():
    BANDERA_RELE4.write_text("off\n")
    aplicar_reles()
    return redirect(url_for("index"))

def loop_auto():
    while True:
        time.sleep(10)
        try:
            auto_humedad()
        except Exception:
            pass
threading.Thread(target=loop_auto, daemon=True).start()

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    def loop_auto():
        while True:
            try:
                auto_humedad()
            except Exception as e:
                print(f"ERROR en auto_humedad: {e}")
            time.sleep(10)
    threading.Thread(target=loop_auto, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
