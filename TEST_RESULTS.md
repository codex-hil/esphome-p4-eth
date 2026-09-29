# Test results — 2026-09-29

Status: **ETHERNET/SERVICES WORKING; PHYSICAL ACCEPTANCE INCOMPLETE**.
The base bringup-002 passed network acceptance. The board currently runs the
temporary `gpio-test-003` profile at 192.168.2.14, awaiting physical GPIO readings.
No claim of GPIO, cold-start reliability, USB-independent or PoE operation is made.

| Acceptance item | Result | Evidence / reason |
|---|---|---|
| ESPHome firmware builds | PASS | logs/ota-build-002.log; manifests/build-hardware-002.json |
| Current clean checkout/state rebuild | PASS | logs/clean-reproduction-20260929.log; manifests/build-clean-20260929.json; committed source 8b157ab, fresh state, public compile fixture |
| USB flash and verification | PASS | logs/usb_flash.log and logs/phy-address1-flash.log |
| ROM/bootloader/app UART capture | PASS | logs/first_boot.log; logs/ethernet-boot.log |
| IP101 identity and initialization | PASS after correction | MDIO 0243:0c54 at addr1; logs/mdio-scan-boot.log |
| Ethernet link / negotiation | PASS | logs/ethernet-boot.log: 100Mb/s full duplex |
| DHCP-assigned IPv4 | PASS | Dynamic config, Ethernet connected event: 192.168.2.14; no static IP configured |
| Independent LAN ping / neighbour | PASS | logs/ethernet.log: 5/5 replies, MAC e8:f6:0a:e7:fe:3f on enp1s0 |
| Encrypted native API + live build | PASS | logs/api-test-001.log and logs/ota_test.log |
| MQTT live state/availability/restart | PASS | logs/mqtt-restart-final.log: offline → online, uptime reset, fresh build after reboot |
| MQTT reconnect after broker restart | PASS | logs/mqtt-service-reconnect.log: recovered at uptime184, no device reboot |
| MQTT unexpected-loss Last Will | NOT RUN | Requires controlled loss of power/network; graceful shutdown tested |
| Ethernet OTA + new running firmware | PASS | logs/ota_test.log: explicit IPv4 upload, API bringup-002; logs/mqtt-after-ota.log |
| GPIO2 physical measurement | PENDING | gpio-test-003 installed by Ethernet OTA; API verified; MQTT OFF received; awaiting meter LOW/HIGH readings and instrument model |
| 10 true cold starts / reliability | NOT RUN | 0/10; no verified remotely controlled power setup |
| USB-disconnected operation | NOT RUN | Independent power arrangement unconfirmed |
| PoE-only boot/API/MQTT/OTA | NOT RUN | Populated PD and compatible PSE unconfirmed |

## Observed hardware and software

| Field | Evidence |
|---|---|
| Board | **Waveshare ESP32-P4-ETH** confirmed by user front/rear photographs; PCB revision unreadable |
| SoC | ESP32-P4 revision **3.2**, 400MHz, ROM eco7-20260109 |
| Flash | ROM detected **32MB**, manufacturer c8, device 4019 |
| PSRAM | 32MB specified for expected part; not enabled or physically tested |
| ESPHome / ESP-IDF | **2026.9.0 / 5.5.5** |
| Compiler / esptool | RISC-V GCC 14.2.0 esp-14.2.0_20260121 / 5.3.1 |
| PHY | **IP101**, measured addr **1**, ID registers **0243:0c54** |
| Wiring | MDC31, MDIO52, REF_CLK50 input from PHY, reset51 |
| Network | **192.168.2.14**, MAC **E8:F6:0A:E7:FE:3F**, 100Mb/s full duplex |
| USB | CH343-family bridge **1a86:55d3**, serial **5C93016778**, interface00 |
| Serial path | /dev/serial/by-id/usb-1a86_USB_Single_Serial_5C93016778-if00 → ttyACM0 |
| GPIO actually tested | None; candidate GPIO2, P1 contact15 |
| MQTT broker | Authenticated test Mosquitto on host **192.168.2.107:1884**, restricted topic ACL; user service p4-eth-test-mqtt (not enabled at host boot) |
| Firmware | bringup-002, 16MB address space with two OTA slots; private credentials local |
| Source patches in final firmware | **None**; temporary read-only diagnostic patch fully reverted |
| Cold starts / no-USB / PoE | **NOT RUN**, physical actions/equipment pending |

## Investigation and evidence limits

The initial schematic-derived PHY address 0 failed: `power up timeout` followed
by `init phy failed`. This remains in the full first_boot.log; it is not hidden.
A read-only MDIO scan found exactly one PHY at address 1; all other addresses
returned ffff:ffff. Changing only phy_addr to 1 resolved initialization. The scan
patch was removed before the successful Ethernet and OTA builds. The physical
reason for the PDF/board discrepancy is not established; no random pin changes
or delay workarounds were used. See patches/README.md.

Serial opening plus the explicitly requested RTS reset can produce an initial
partial boot followed by the complete captured boot. These are intentional resets,
not demonstrated intermittent cold-boot failures. ROM POWERON reset reason alone
does not prove supply was removed; therefore no reset is counted as a cold cycle.

API tests authenticate using the private Noise key and read the build entity.
MQTT tests reject retained-only evidence, match MAC/build, and require offline,
online, lower uptime and a fresh post-reboot build after the command. OTA transferred
in approximately 2 seconds; upload success was followed by API/MQTT confirmation
of bringup-002. Topic captures are in mqtt-observation.log. Host credentials and
firmware remain ignored by Git. First preparation build manifests are historical
compile-only fixtures; build-hardware-002.json identifies the deployed image.

Safe mode is configured, but deliberate repeated-failed-boot activation has not
been tested. PSRAM and unused peripheral buses are outside the demonstrated scope.
The other CP2102/FT2232 devices were not reset, flashed or used in this task.
No eFuses/security settings were modified. Existing dialout membership was
activated in a child via `sg`; host permissions were not changed.

## Cold-start evidence table

Each row requires real power removal, serial evidence, DHCP corroboration, a
successful authenticated API call and fresh MQTT traffic. Time is measured from
power application until all required services are ready. Software resets do not
count. Record file/timestamp references and investigate every intermittent failure.

| cycle | boot | ETH | DHCP | API | MQTT | boot time | notes |
|---|---|---|---|---|---|---|---|
| 1 | — | — | — | — | — | — | NOT RUN |
| 2 | — | — | — | — | — | — | NOT RUN |
| 3 | — | — | — | — | — | — | NOT RUN |
| 4 | — | — | — | — | — | — | NOT RUN |
| 5 | — | — | — | — | — | — | NOT RUN |
| 6 | — | — | — | — | — | — | NOT RUN |
| 7 | — | — | — | — | — | — | NOT RUN |
| 8 | — | — | — | — | — | — | NOT RUN |
| 9 | — | — | — | — | — | — | NOT RUN |
| 10 | — | — | — | — | — | — | NOT RUN |

## Remaining physical work

1. Confirm PCB silkscreen revision, PoE module/source and GPIO2 test wiring.
2. Measure GPIO2 HIGH/LOW with an independent instrument using the optional test profile.
3. Remove all supply power for 10 genuine cold starts; record each boot and services.
4. Test independent power with USB disconnected; if PoE is available, repeat including OTA using Ethernet cable only.
5. Finalize the base configuration and publish the requested repository after applicable acceptance gates pass.

No GitHub publication has occurred. Access to account codex-hil is available;
publication is deferred because the user requested it after completion.

## Photograph and GPIO preparation update

User photographs confirm the product silkscreen and show unused exposed GPIO
pads. The front six-pin PoE header appears unoccupied; no mounted PD converter
is visible. This does not establish what separate equipment the user has.

Temporary profile `device-gpio-test.yaml` with substitution `build_label=gpio-test-003`
was compiled and uploaded over Ethernet; API and fresh MQTT confirm it runs.
GPIO2 reports OFF, restore mode ALWAYS_OFF. This is software state only: no
independent voltage reading has yet been supplied. The user was asked to measure
pad `2` (above SCL, not 24/25) relative to GND. Hold LOW until that reading arrives,
then command HIGH, obtain a second reading and return LOW. Restore the base
profile after the measurement before cold-start/independent-power acceptance.
Evidence: logs/gpio-ota-003.log, logs/gpio-api-003.log,
logs/gpio-mqtt-observation.log and logs/gpio_test.log. Firmware/private photos
are not committed; photograph hashes are recorded in manifests/hardware.json.
