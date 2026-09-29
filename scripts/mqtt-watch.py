"""Timestamp independent MQTT observations; does not label them as test passes."""
import argparse
import json
from pathlib import Path
import time
import paho.mqtt.client as mqtt
import yaml
p = argparse.ArgumentParser()
p.add_argument('--seconds', type=float, default=300)
p.add_argument('--name', default='p4-eth')
a = p.parse_args()
s = yaml.safe_load(Path('secrets.yaml').read_text())
c = mqtt.Client(client_id=f'p4-observer-{time.time_ns()}')
c.username_pw_set(s['mqtt_username'], s['mqtt_password'])
def connected(client, userdata, flags, rc):
    print(json.dumps({'event': 'broker_connection', 'rc': rc, 'time': time.time()}), flush=True)
    if rc == 0:
        client.subscribe(f'controllers/{a.name}/#', qos=1)
def message(client, userdata, msg):
    print(json.dumps({'time': time.time(), 'topic': msg.topic,
                      'payload': msg.payload.decode(errors='replace'),
                      'retained': bool(msg.retain)}), flush=True)
c.on_connect = connected
c.on_message = message
c.connect(s['mqtt_broker'], int(s['mqtt_port']), 30)
c.loop_start()
try:
    time.sleep(a.seconds)
finally:
    c.disconnect()
    c.loop_stop()
