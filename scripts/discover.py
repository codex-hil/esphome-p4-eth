"""Bounded mDNS discovery; absence is not proof the wired device is offline."""
import argparse
import json
import time
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
p = argparse.ArgumentParser()
p.add_argument('--seconds', type=float, default=10)
a = p.parse_args()
found = set()
class Listener(ServiceListener):
    def add_service(self, zc, kind, name):
        info = zc.get_service_info(kind, name, timeout=2000)
        if info:
            found.add(name)
            print(json.dumps({'service': name, 'addresses': info.parsed_addresses(), 'port': info.port}), flush=True)
    def update_service(self, zc, kind, name):
        self.add_service(zc, kind, name)
    def remove_service(self, zc, kind, name):
        pass
with Zeroconf() as zc:
    browser = ServiceBrowser(zc, '_esphomelib._tcp.local.', Listener())
    time.sleep(a.seconds)
    browser.cancel()
if not found:
    print('No ESPHome mDNS service observed; check serial DHCP log/router lease table.')
    raise SystemExit(1)
