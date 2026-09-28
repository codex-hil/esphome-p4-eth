"""Audit actual SDK configuration and firmware artifacts, not just YAML intent."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('build_dir', type=Path)
p.add_argument('--profile', choices=('production', 'es'), required=True)
a = p.parse_args()
sdk = (a.build_dir / 'sdkconfig.p4-eth').read_text()
expect = {
    'CONFIG_IDF_TARGET': '"esp32p4"',
    'CONFIG_ESPTOOLPY_FLASHSIZE': '"16MB"',
    'CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ': '400' if a.profile == 'production' else '360',
    'CONFIG_ESP_REV_MIN_FULL': '300' if a.profile == 'production' else '0',
    'CONFIG_ETH_USE_ESP32_EMAC': 'y',
    'CONFIG_ETH_PHY_INTERFACE_RMII': 'y',
    'CONFIG_ESP_CONSOLE_UART_NUM': '0',
}
for key, value in expect.items():
    if f'{key}={value}' not in sdk.splitlines():
        raise SystemExit(f'FAIL: {key} must be {value}')
for key in ('CONFIG_SECURE_BOOT', 'CONFIG_SECURE_FLASH_ENC_ENABLED'):
    if f'{key}=y' in sdk.splitlines():
        raise SystemExit(f'FAIL: irreversible security feature enabled: {key}')
if ('CONFIG_ESP32P4_SELECTS_REV_LESS_V3=y' in sdk.splitlines()) != (a.profile == 'es'):
    raise SystemExit('FAIL: incorrect silicon layout')
artifacts = {}
for name in ('firmware.factory.bin', 'firmware.ota.bin', 'firmware.elf'):
    f = a.build_dir / 'build' / name
    artifacts[name] = {'bytes': f.stat().st_size, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()}
result = {'status': 'PASS_BUILD_ONLY', 'profile': a.profile,
          'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'esphome': '2026.9.0', 'idf': '5.5.5', 'sdkconfig': expect,
          'sdkconfig_sha256': hashlib.sha256(sdk.encode()).hexdigest(),
          'artifacts': artifacts, 'hardware_tests': 'NOT_RUN'}
print(json.dumps(result, indent=2))
