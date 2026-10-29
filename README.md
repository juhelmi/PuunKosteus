# PuunKosteus
Puun kosteuden seuranta sähkön johtavuuden perusteella

MicroPython (Pico 2 W) firmware: reads two resistances via ADS1115 (I2C) once an hour,
serves a history graph on a web page (JS client side, `/data` JSON) and publishes via MQTT.
Copy `*.py` to the Pico, install `umqtt.simple` (`mpremote mip install umqtt.simple`),
and edit `config.py` (WiFi, MQTT, pins, `MEASURE_MS`, `INTERVAL_S`).
