import json
import time
import network
import socket
from machine import Pin, I2C
from umqtt.simple import MQTTClient

import config
from ads1115 import ADS1115
from measure import measure

INDEX_HTML = b"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>PuunKosteus</title></head><body><h1>PuunKosteus</h1>
<canvas id="c" width="800" height="400" style="border:1px solid #888"></canvas>
<pre id="t"></pre>
<script>
const col=["#d33","#33d","#3a3","#a3a"];
fetch("/data").then(r=>r.json()).then(d=>{
 const c=document.getElementById("c"),x=c.getContext("2d"),W=c.width,H=c.height;
 const names=d.names,h=d.history;
 let max=1;h.forEach(p=>p.r.forEach(v=>{if(v!==null&&v>max)max=v}));
 const n=Math.max(h.length-1,1);
 names.forEach((nm,i)=>{x.strokeStyle=col[i%4];x.beginPath();let s=false;
  h.forEach((p,k)=>{const v=p.r[i];if(v===null)return;
   const px=k/n*(W-20)+10,py=H-10-v/max*(H-20);
   if(s)x.lineTo(px,py);else{x.moveTo(px,py);s=true}});x.stroke();
  x.fillStyle=col[i%4];x.fillText(nm,10+i*60,12)});
 x.fillStyle="#000";x.fillText("max "+Math.round(max)+" ohm",W-120,12);
 document.getElementById("t").textContent=h.slice(-10).map(p=>
  new Date(p.t*1000).toLocaleString()+"  "+p.r.join("  ")).join("\\n");
});
</script></body></html>"""

history = []


def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        for _ in range(30):
            if wlan.isconnected():
                break
            time.sleep(1)
    return wlan


def do_measure(adc):
    res = []
    for ch in config.CHANNELS:
        r = measure(adc, ch, Pin, config.MEASURE_MS, config.VCC, config.R_REF)
        res.append(None if r is None else round(r))
    entry = {"t": time.time(), "r": res}
    history.append(entry)
    if len(history) > config.HISTORY_LEN:
        history.pop(0)
    return entry


def publish(entry):
    try:
        c = MQTTClient(config.MQTT_CLIENT_ID, config.MQTT_BROKER,
                       port=config.MQTT_PORT, user=config.MQTT_USER,
                       password=config.MQTT_PASSWORD)
        c.connect()
        payload = {"t": entry["t"]}
        for ch, r in zip(config.CHANNELS, entry["r"]):
            payload[ch["name"]] = r
        c.publish(config.MQTT_TOPIC, json.dumps(payload))
        c.disconnect()
    except OSError as e:
        print("MQTT error", e)


def serve(srv):
    try:
        cl, _ = srv.accept()
    except OSError:
        return
    try:
        cl.settimeout(2)
        req = cl.recv(512)
        if req.startswith(b"GET /data"):
            body = json.dumps({"names": [c["name"] for c in config.CHANNELS],
                               "history": history})
            cl.send(b"HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n")
            cl.send(body)
        else:
            cl.send(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
            cl.send(INDEX_HTML)
    except OSError:
        pass
    finally:
        cl.close()


def main():
    wifi_connect()
    try:
        import ntptime
        ntptime.settime()
    except Exception as e:
        print("NTP error", e)
    i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA), scl=Pin(config.I2C_SCL))
    adc = ADS1115(i2c, config.ADS_ADDR)
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", config.HTTP_PORT))
    srv.listen(2)
    srv.settimeout(0.5)
    next_t = time.ticks_ms()
    while True:
        if time.ticks_diff(time.ticks_ms(), next_t) >= 0:
            entry = do_measure(adc)
            if not network.WLAN(network.STA_IF).isconnected():
                wifi_connect()
            publish(entry)
            next_t = time.ticks_add(time.ticks_ms(), config.INTERVAL_S * 1000)
        serve(srv)


main()
