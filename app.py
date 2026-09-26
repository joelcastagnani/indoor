import subprocess
import sys
from pathlib import Path

from flask import Flask, redirect, url_for

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent
proc = None


def corriendo():
    return proc is not None and proc.poll() is None


@app.get("/")
def index():
    estado = "prendido" if corriendo() else "apagado"
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Indoor</title>
  <style>
    body {{ font-family: sans-serif; max-width: 28rem; margin: 3rem auto; }}
    .estado {{ font-size: 1.2rem; margin-bottom: 1.5rem; }}
    form {{ display: inline-block; margin-right: 0.5rem; }}
    button {{ padding: 0.6rem 1.2rem; font-size: 1rem; }}
  </style>
</head>
<body>
  <h1>Indoor</h1>
  <p class="estado">Cámara: <strong>{estado}</strong></p>
  <form method="post" action="/iniciar"><button type="submit">Iniciar</button></form>
  <form method="post" action="/detener"><button type="submit">Detener</button></form>
</body>
</html>
"""


@app.post("/iniciar")
def iniciar():
    global proc
    if not corriendo():
        proc = subprocess.Popen(
            [sys.executable, str(ROOT / "foto_loop.py")],
            cwd=ROOT,
        )
    return redirect(url_for("index"))


@app.post("/detener")
def detener():
    global proc
    if corriendo():
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
