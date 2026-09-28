"""Send a non-retained GPIO2 command. Does not claim a physical measurement."""
import argparse
from pathlib import Path
import paho.mqtt.publish as publish
import yaml
p = argparse.ArgumentParser()
p.add_argument('state', choices=('ON', 'OFF'))
p.add_argument('--name', default='p4-eth')
a = p.parse_args()
s = yaml.safe_load(Path('secrets.yaml').read_text())
publish.single(f'controllers/{a.name}/command/gpio2', a.state, qos=1, retain=False,
               hostname=s['mqtt_broker'], port=int(s['mqtt_port']),
               auth={'username': s['mqtt_username'], 'password': s['mqtt_password']})
print('Command delivered to broker; record independent GPIO voltage measurement.')
