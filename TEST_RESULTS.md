# Test results

Status: **PREPARATION COMPLETE / PHYSICAL ACCEPTANCE PENDING**.
As of 2026-09-28 the user has not connected the Waveshare ESP32-P4-ETH; connection
is planned for tomorrow. No hardware pass can be inferred from these builds.

| Acceptance item | Result | Evidence / reason |
|---|---|---|
| ESPHome builds, production >=3.0 | PASS | logs/build-production.log; manifests/build-production.json |
| ESPHome builds, engineering sample <3.0 | PASS | logs/build-es.log; manifests/build-es.json |
| GPIO profile YAML validation | PASS | logs/config-gpio.log |
| Rebuild from clean checkout/state | PENDING | Clean reproduction in progress |
| USB flash | NOT RUN | Board absent |
| Reliable boot and serial logger | NOT RUN | Board absent |
| PHY initialization and link | NOT RUN | Board absent |
| DHCP / host ping / neighbour | NOT RUN | Board absent |
| Encrypted native API | NOT RUN | Host probe prepared; board absent |
| MQTT availability, live state, command | NOT RUN | Host subscriber prepared; board absent |
| Ethernet OTA + new live build value | NOT RUN | Board absent |
| Physical GPIO2 voltage/action | NOT RUN | Candidate verified from schematic; instrument/wiring pending |
| 10 cold starts | NOT RUN | Power arrangement pending |
| USB-disconnected operation | NOT RUN | Independent supply pending |
| PoE-only API/MQTT/OTA | NOT RUN | PD module + compatible PSE presence unknown |

Builds use public compile fixtures, not deployable credentials. The host scripts
have been checked for imports/CLI operation only; their real-device behaviour
remains unvalidated until executed against the board. No source patches/external
components. Configuration choices are documented in docs/SUPPORT.md.

## Hardware report (fill from observations)

| Field | Current evidence |
|---|---|
| Exact hardware physically detected | None: no P4 connected |
| Expected board | Waveshare ESP32-P4-ETH; schematic drawing rev1.1 |
| Actual PCB/chip revision | Unknown |
| ESPHome / ESP-IDF | 2026.9.0 / 5.5.5 |
| Compiler | RISC-V GCC 14.2.0 / esp-14.2.0_20260121 |
| PHY configuration | IP101, addr0, MDC31, MDIO52, REF_CLK50 input, reset51; not measured |
| Flash / PSRAM | Nominal 32MB / 32MB from official documentation; ROM verification pending |
| Firmware flash address space | 16MB, two OTA slots; PSRAM not enabled |
| DHCP IP / MAC | Not obtained |
| USB VID/PID/path | Not observed; expected CH343 UART bridge |
| GPIO actually tested | None; candidate GPIO2/P1 contact15 |
| OTA / MQTT result | NOT RUN / NOT RUN |
| Cold starts / USB-independent result | 0/10 / NOT RUN |
| PoE-only result | NOT RUN; hardware/source availability unknown |
| Remaining issues | Physical identity, service/network tests, GPIO observation, power/PoE tests |

Host baseline: CP2102 10c4:ea60 and FT2232 0403:6010 are already attached other
hardware; neither has been accessed/reset for this task. Host enp1s0 reports link
UP; this does not prove a link to the absent board. Raw inventory is local in
logs/host_inventory.log. No new P4 USB VID/PID is asserted.

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

## Next session

1. Compare USB inventory; identify actual PCB/PoE population and stable serial path.
2. Read ROM chip revision/flash ID; select production vs ES, confirm schematic match.
3. Generate local credentials, set broker, rebuild and flash; capture complete boot.
4. Validate Ethernet independently, native API and MQTT including observable restart.
5. Change build label, OTA via explicit IPv4, verify new live API/MQTT value.
6. Measure GPIO2 HIGH/LOW independently, then return to final base profile.
7. Complete cold starts and independent-power/PoE-only tests as applicable.
8. Record final configuration/identity, clean rebuild, review secrets, publish repository
   on `codex-hil` only after acceptance. No publication has occurred yet.
