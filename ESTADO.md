# Estado actual del indoor

## Hardware
- ESP32 en /dev/ttyUSB0
- Relé 4 canales (activo bajo)
  - K1: Pin 23 (manual)
  - K2: Pin 18
  - K3: Pin 19
  - K4: Pin 5
- Cámara: Logitech C920
- Sensor: AHT10 (I2C 0x38)

## Automatización (v2)
- K2: humedad >= 65 %
- K3: humedad >= 75 %
- K4: temperatura >= 24 °C
- Se evalúa cada 10 segundos

## Servicios (notebook)
- indoor.service → app.py
- indoor-video.service → video_loop.py