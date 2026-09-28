"""Verify encrypted native API, identity and a LIVE build diagnostic."""
import argparse
import asyncio
import json
from pathlib import Path
import aioesphomeapi
import yaml

async def main():
    p = argparse.ArgumentParser()
    p.add_argument('ip')
    p.add_argument('--expect-build', required=True)
    p.add_argument('--expect-mac', required=True)
    args = p.parse_args()
    secret = yaml.safe_load(Path('secrets.yaml').read_text())
    client = aioesphomeapi.APIClient(args.ip, 6053, None, noise_psk=secret['api_encryption_key'])
    try:
        await asyncio.wait_for(client.connect(login=True), 15)
        info = await client.device_info()
        if info.mac_address.lower() != args.expect_mac.lower():
            raise RuntimeError(f'Wrong device MAC: {info.mac_address}')
        entities, _ = await client.list_entities_services()
        build = next(e for e in entities if isinstance(e, aioesphomeapi.TextSensorInfo) and e.name == 'Build')
        observed = asyncio.get_running_loop().create_future()
        def state_update(state):
            if state.key == build.key and getattr(state, 'state', None) == args.expect_build and not observed.done():
                observed.set_result(state.state)
        client.subscribe_states(state_update)
        value = await asyncio.wait_for(observed, 25)
        print(json.dumps({'api': 'PASS', 'mac': info.mac_address, 'esphome': info.esphome_version, 'build': value}))
    finally:
        await client.disconnect()

asyncio.run(main())
