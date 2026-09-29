# Waveshare ESP32-P4-ETH / ESPHome controller base

**Physical bring-up in progress.** Connected ESP32-P4 rev3.2 with 32MB flash.
The measured PHY address is **1**, not the initial schematic-derived assumption 0.
Ethernet (100Mb/s full duplex), DHCP, host ping, native API and MQTT restart have
passed. See [TEST_RESULTS.md](TEST_RESULTS.md) for OTA and remaining GPIO/power gates.
Publication to `codex-hil/esphome-p4-eth` remains deferred until acceptance.

Base functionality: Ethernet/DHCP, UART logging, encrypted native API,
authenticated OTA, MQTT diagnostics and restart, and safe mode. No Wi-Fi,
web server, RS485, CAN, display, or unnecessary sensor drivers.

[Hardware evidence and pin map](docs/HARDWARE.md) ·
[Source/support audit and findings](docs/SUPPORT.md)

## Environment and build

Supported reproducible build host: Linux x86_64 with Git and an installed Nix
(flake support). This host already has Nix; no global pip/apt installs or Docker
are needed. The flake pins ESPHome 2026.9.0, ESP-IDF 5.5.5, Python dependencies,
RISC-V GCC 14.2.0 / esp-14.2.0_20260121, and MQTT client/broker tools. Initial
Nix downloads and IDF component downloads need Internet access.

```bash
cd /home/codex-hil/esphome-p4-eth  # or your fresh checkout
./scripts/nix-exec.sh true       # instantiate pinned environment
./scripts/esphome version
./scripts/init-secrets.py        # refuses to overwrite secrets.yaml
chmod 600 secrets.yaml
# Edit MQTT broker/port/username/password in secrets.yaml locally.
./scripts/esphome config device.yaml
./scripts/build.sh device.yaml
```

For compilation without a board/broker, `cp secrets.example.yaml secrets.yaml`
provides explicitly public test credentials and a TEST-NET broker address. The
preparation builds use those fixtures. **Replace the fixture with generated
private credentials and rebuild before flashing.** For the prepared fixture:

```bash
mv secrets.yaml .state/compile-fixture.local.yaml
./scripts/init-secrets.py
# Now edit MQTT settings locally, then rebuild.
```

Firmware embeds credentials;
keep `.state/`, `.esphome/`, `secrets.yaml` and firmware out of Git.

Use `device-es.yaml` for ROM-detected chip revision <3.0. Use `device.yaml` for
>=3.0. Production and ES layouts are incompatible. Both use only the first
16MB of the nominal 32MB flash for non-experimental OTA. PSRAM is not required.
Do not change pin assignments based on examples for a different board.

## Identify the board before USB access

```bash
./scripts/inventory.sh | tee logs/host_inventory.log
```

Compare inventory before/after plugging in. Match physical PCB markings and the
CH343 bridge to a stable `/dev/serial/by-id/...` (or uniquely verified `by-path`)
path, record VID/PID, serial/interface, PCB revision and PoE module. The attached P4 bridge is `1a86:55d3`, serial `5C93016778`,
`/dev/serial/by-id/usb-1a86_USB_Single_Serial_5C93016778-if00`. The
CP2102 and FT2232 are other devices: never use enumeration order.
Only after identifying the P4:

```bash
PORT=/dev/serial/by-id/REPLACE_WITH_VERIFIED_P4_BRIDGE
./scripts/esphome --python -m esptool --chip esp32p4 --port "$PORT" chip-id
./scripts/esphome --python -m esptool --chip esp32p4 --port "$PORT" flash-id
```

These ROM probes reset the selected board but do not program it. Record full
output in `logs/chip_identity.log`. Select the matching YAML, confirm detected
flash size is at least the configured 16MB, and retain chip MAC/revision. If
there is no unique USB serial, record the verified topology path. Host serial
access must already be granted; do not alter host permissions or other devices.

## Flash and capture a complete boot

```bash
CONFIG=device.yaml  # or device-es.yaml after ROM revision check
./scripts/build.sh "$CONFIG"
set -o pipefail
./scripts/esphome upload "$CONFIG" --device "$PORT" 2>&1 | tee logs/usb_flash.log
# First remove/archive the NOT RUN marker, never overwrite real evidence.
mv logs/first_boot.log logs/first_boot.pending
./scripts/esphome --python scripts/serial-capture.py "$PORT" \
  --seconds 120 --output logs/first_boot.log
```

Once capture says ready, press RST to include ROM, bootloader and app startup.
For ongoing decoded logs: `./scripts/esphome logs "$CONFIG" --device "$PORT"`.
Do not run two serial readers at once. Preserve raw output before interpreting it.

If auto-download fails, first check port identity, permission, cable and competing
readers. Manual download: hold BOOT, press/release RST, then release BOOT and retry
the same upload. If needed, use ESPHome's generated factory image with esptool
**after checking the factory layout and application image**:

```bash
FACTORY=.state/nix/build/p4-eth/build/firmware.factory.bin
./scripts/esphome --python scripts/verify-build.py .state/nix/build/p4-eth \
  --profile production  # use es for the ES silicon profile
./scripts/esphome --python -m esptool --chip esp32p4 \
  image-info .state/nix/build/p4-eth/build/firmware.ota.bin
./scripts/esphome --python -m esptool --chip esp32p4 --port "$PORT" \
  write-flash 0x0 "$FACTORY"
```

The layout checker compares each segment against the merged factory image.
`image-info` accepts the OTA application image, not the padded factory image.
The combined factory binary includes the correct P4 bootloader offset; do not
flash an OTA binary at 0. Never use `--force`, eFuse/OTP writes, secure boot,
flash encryption or JTAG disablement. No full flash erase is normally necessary.

## Ethernet and native API

In serial output require successful IP101 initialization, link up, negotiated
speed/duplex, MAC and DHCP address. A configured PHY type is not proof it was
detected. Match the lease to the device MAC. Preserve these lines in ethernet.log.
The profile has no static address, so a nonzero assigned address should also be
corroborated by DHCP logs/capture or the router's lease table.

```bash
./scripts/esphome --python scripts/discover.py
# Read actual values from serial + router lease table, never guess:
IP=REPLACE_WITH_DHCP_ADDRESS
MAC=REPLACE_WITH_DEVICE_MAC
ping -c 5 "$IP" | tee -a logs/ethernet.log
ip route get "$IP" | tee -a logs/ethernet.log
ip neigh show to "$IP" | tee -a logs/ethernet.log
./scripts/esphome --python scripts/api-check.py "$IP" \
  --expect-mac "$MAC" --expect-build bringup-001 | tee -a logs/ethernet.log
```

Use the same L2 LAN for direct neighbour/MAC verification. Across a router the
host sees the gateway MAC; record that limitation and inspect the router/switch.
API check actually authenticates and reads a live diagnostic; open port 6053
alone is not success. `Ethernet Connected` means IP-ready, not raw link carrier.

## MQTT

Set credentials only in ignored `secrets.yaml`. Topic root:
`controllers/p4-eth`; retained availability is `availability`, diagnostics are
`diagnostics/{uptime,ip,mac,esphome,build,reset_reason,ethernet_connected}`, commands
are `command/restart` and `command/safe_mode`. Discovery is disabled to keep this
base independent of a Home Assistant instance. API/MQTT client absence does not
cause scheduled reboot loops.

The host subscriber records topic, payload, timestamp and retained flag. It
requires live uptime (old retained messages cannot satisfy this), checks identity,
and with `--restart` publishes non-retained `PRESS`, then requires fresh offline →
online availability plus reduced uptime and the expected build.

```bash
./scripts/esphome --python scripts/mqtt-check.py --expect-mac "$MAC" \
  --expect-build bringup-001 --restart 2>&1 | tee logs/mqtt_test.log
```

This is an intentional observable restart. For Last Will verification separately
remove device power while subscribed, observe broker-published offline after its
keepalive timeout, restore power and observe online/live state. A graceful restart
checks shutdown availability, not unexpected-loss Last Will behaviour.

If no broker is available, provision the pinned Mosquitto on a chosen LAN address
in a separate terminal. Keep it running through all tests:

```bash
mkdir -p .state/broker
chmod 700 .state/broker
./scripts/nix-exec.sh mosquitto_passwd -c .state/broker/passwd p4-test
# Replace HOST_LAN_IP with this host's actual LAN address (not 0.0.0.0).
printf 'listener 1883 HOST_LAN_IP\nallow_anonymous false\npassword_file %s/.state/broker/passwd\n' \
  "$PWD" > .state/broker/mosquitto.conf
./scripts/nix-exec.sh mosquitto -c .state/broker/mosquitto.conf -v
```

Configure this address/user/password in secrets.yaml and rebuild before flashing.
This profile uses ordinary MQTT on a trusted test LAN; Internet-facing brokers
require a separately configured TLS profile. Do not print secrets into evidence.

## Mandatory Ethernet OTA test

After baseline API/MQTT pass, change `build_label: bringup-001` to
`build_label: bringup-002` in device.yaml (also inherited by the ES profile).
Rebuild the SAME silicon profile. Keep serial/host MQTT capture active, then:

```bash
./scripts/build.sh "$CONFIG"
./scripts/esphome upload "$CONFIG" --device "$IP" 2>&1 | tee logs/ota_test.log
# After reboot/reconnect:
./scripts/esphome --python scripts/api-check.py "$IP" \
  --expect-mac "$MAC" --expect-build bringup-002 | tee -a logs/ota_test.log
./scripts/esphome --python scripts/mqtt-check.py --expect-mac "$MAC" \
  --expect-build bringup-002 | tee -a logs/ota_test.log
```

Use the explicit IPv4 to ensure this is network OTA. A successful upload alone
is not a pass: require reboot and new live build value over both services.

## GPIO, cold starts and USB independence

GPIO2 (P1 contact 15, silkscreen `2`) is the schematic-verified candidate.
Power off while connecting a high-impedance meter/analyzer to GPIO2 and GND;
confirm the actual board revision and no HAT/peripheral uses that net. No usable
programmable onboard LED is shown. Enable `common/gpio-test.yaml` via the provided
`device-gpio-test.yaml`. For ES use `device-es-gpio-test.yaml`. Build the selected profile, recheck
final sdkconfig, then upload it over Ethernet before sending GPIO commands.

```bash
./scripts/build.sh device-gpio-test.yaml  # or device-es-gpio-test.yaml
./scripts/esphome upload device-gpio-test.yaml --device "$IP"  # match profile
./scripts/esphome --python scripts/mqtt-gpio.py ON
# Measure HIGH now.
./scripts/esphome --python scripts/mqtt-gpio.py OFF
# Measure LOW now.
```

These commands publish without retention to `controllers/p4-eth/command/gpio2`.
Observe actual pin voltage in both states and log the
instrument, wiring, measurements and timestamps in `logs/gpio_test.log`. A state
echo alone cannot prove a GPIO test. Return to the base profile after the test.

Perform 10 true cold starts, not software restarts: disconnect **all** power
sources, allow rails to fall, reapply power. Keep a host subscriber running.
For each run capture boot/PHY/link/DHCP plus API and fresh MQTT evidence. Measure
boot time from power application to all services ready. Fill the table in
TEST_RESULTS.md and keep raw evidence in power_cycle_test.log. If automation is
unavailable, perform the sequence manually. Investigate any failure before pass.

With compatible independent power, remove USB completely, keep Ethernet and
repeat ping/API/MQTT plus OTA. If the board has a populated PoE PD and a verified
compatible active source, repeat using only the PoE Ethernet cable and verify
OTA as well. Record actual PSU/PD/PSE models. Without those, mark the relevant
test blocked/not applicable with reason; Ethernet success does not prove PoE.

## Clean reproduction and handoff

Use a fresh checkout and an empty project state; Nix store reuse is intentional.
A successful clean build is not a physical acceptance claim.

```bash
./scripts/reproduce.sh /absolute/path/to/new-checkout
```

Before publication: complete all applicable TEST_RESULTS gates, replace pending
markers with real logs, finalize hardware identity/settings, review hashes and
scan tracked content for secrets. Then create the requested GitHub repository
on the authorized `codex-hil` account. Do not publish firmware/credentials/raw LAN
captures. User requested publication after completion, so it is deferred while
physical tests are pending.
