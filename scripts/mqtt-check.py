"""Host MQTT probe. --restart sends one non-retained command to the designated device."""
import argparse
import json
from pathlib import Path
import threading
import time
import paho.mqtt.client as mqtt
import yaml
p = argparse.ArgumentParser()
p.add_argument('--name', default='p4-eth')
p.add_argument('--expect-build', required=True)
p.add_argument('--expect-mac', required=True)
p.add_argument('--restart', action='store_true')
p.add_argument('--timeout', type=int, default=90)
a = p.parse_args()
s = yaml.safe_load(Path('secrets.yaml').read_text())
prefix = f'controllers/{a.name}'
client = mqtt.Client(client_id=f'p4-check-{time.time_ns()}')
client.username_pw_set(s['mqtt_username'], s['mqtt_password'])
condition = threading.Condition()
messages = []
def on_connect(c, userdata, flags, rc):
    if rc != 0:
        print(json.dumps({'connection_error': rc}), flush=True)
        return
    c.subscribe(prefix + '/#', qos=1)
def on_message(c, userdata, msg):
    entry = {'time': time.time(), 'topic': msg.topic, 'payload': msg.payload.decode(errors='replace'), 'retained': bool(msg.retain)}
    print(json.dumps(entry), flush=True)
    with condition:
        messages.append(entry)
        condition.notify_all()
def wait_for(predicate, start=0):
    end = time.monotonic() + a.timeout
    with condition:
        while True:
            for m in messages:
                if m['time'] >= start and predicate(m):
                    return m
            remaining = end - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Required MQTT evidence missing')
            condition.wait(remaining)
def topic(suffix, payload=None, live=False):
    return lambda m: m['topic'] == prefix + suffix and (payload is None or m['payload'].lower() == payload.lower()) and (not live or not m['retained'])
client.on_connect = on_connect
client.on_message = on_message
client.connect(s['mqtt_broker'], int(s['mqtt_port']), keepalive=30)
client.loop_start()
try:
    # MAC/build may be retained; live uptime below is mandatory before command.
    wait_for(topic('/diagnostics/mac', a.expect_mac))
    wait_for(topic('/diagnostics/build', a.expect_build))
    wait_for(topic('/availability', 'online'))
    old = wait_for(topic('/diagnostics/uptime', live=True))
    if a.restart:
        # Ensure pre-command uptime is high enough to distinguish a reset.
        old = wait_for(lambda m: topic('/diagnostics/uptime', live=True)(m) and float(m['payload']) > 30)
        start = time.time()
        result = client.publish(prefix + '/command/restart', 'PRESS', qos=1, retain=False)
        result.wait_for_publish(timeout=10)
        offline = wait_for(topic('/availability', 'offline', live=True), start)
        online = wait_for(topic('/availability', 'online', live=True), offline['time'])
        wait_for(lambda m: topic('/diagnostics/uptime', live=True)(m) and float(m['payload']) < float(old['payload']), online['time'])
        wait_for(topic('/diagnostics/build', a.expect_build, live=True), online['time'])
    print(json.dumps({'mqtt': 'PASS', 'restart_test': a.restart}), flush=True)
finally:
    client.disconnect()
    client.loop_stop()
