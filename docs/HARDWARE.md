# Hardware evidence — physical bring-up 2026-09-29

Sources inspected on 2026-09-28:

- [Waveshare product documentation](https://docs.waveshare.com/ESP32-P4-ETH)
- [Official schematic + PCB drawings, 3 pages](https://files.waveshare.com/wiki/ESP32-P4-ETH/ESP32-P4-ETH-datasheet.pdf)
- [Vendor ESP-IDF examples](https://github.com/waveshareteam/ESP32-P4-Platform/tree/6f78fa810ec505048c1941e3d09cefc9f29129bd/examples/esp-idf/11_ethernetbasic)
- [ESPHome Ethernet](https://esphome.io/components/ethernet/)
- [ESPHome ESP32](https://esphome.io/components/esp32/)

The PDF PCB drawing says **Rev1.1**. This does not identify the user's board revision.
The connected chip is rev3.2, ROM flash ID c8:4019, 32MB. PCB silkscreen revision
and populated PoE module still need physical confirmation. A USB descriptor alone cannot prove the board model.

| Item | Schematic-derived configuration | Physical observation |
|---|---|---|
| SoC | U6 ESP32-P4NRW32, 32MB stacked PSRAM | Pending |
| Flash | U7 GD25Q256 = 32MB | Pending ROM flash-id |
| PHY | U10 IP101GRI, RMII | Pending PHY identity/init |
| Address | Initially inferred as 0 from R65/R63 in the PDF | **Measured 1**, ID registers 0243:0c54; address 0 is absent |
| MDC / MDIO | GPIO31 / GPIO52 | Pending |
| REF_CLK | GPIO50, 50MHz from IP101 pin 14 to P4, CLK_EXT_IN | Pending |
| PHY reset | GPIO51 to active-low RESET pin 32 | Pending |
| RMII data | TXD0=34, TXD1=35, TX_EN=49, RXD0=29, RXD1=30, CRS_DV=28 | Pending |
| USB programming | H2 Type-C → U4 CH343P → UART0, TX37/RX38 | VID/PID/path pending |
| BOOT / RESET | GPIO35 / ESP_EN | Pending |
| LED1 | Supply indicator, not a programmable GPIO LED | Pending |
| GPIO test candidate | GPIO2, P1 schematic contact **15**, silkscreen `2` | Not yet tested |

The P1 symbol numbers the two rows 1–20 and 21–40. Do not assume Raspberry Pi
header numbering. GPIO2 has only the U6 and P1 connection in this schematic; it
is not a P4 strapping pin or attached to an onboard peripheral. Confirm this for
the actual revision and remove any HAT/peripheral before enabling the optional
test package. Use a high-impedance 3.3V-compatible meter/analyzer with common GND;
never infer voltage from an ESPHome switch state. Record measured LOW/HIGH levels.
Do not use BOOT as a GPIO test: it shares GPIO35 with RMII TXD1.

Vendor example Kconfig defaults to PHY address 1, and its CI file uses classic
ESP32 pins 23/18/5. Those are generic example defaults, not this PCB's assignments.
The initial PDF interpretation suggested address 0, but the actual attached board
responds only at address 1. The full read-only MDIO scan is preserved. Final YAML
uses the measured address 1. The physical cause of the schematic/board discrepancy
is not established; do not claim a specific strap-population change without inspection.

Initial firmware uses only the first 16MB of physical flash. ESPHome rejects
32MB+OTA without the IDF experimental option; no experimental option is enabled.
PSRAM is physically specified but not enabled/required by this minimal controller.
Neither unused memory nor the remaining peripherals are claimed tested.

`device.yaml`: rev >=3.0 layout, minimum 3.0 explicitly selected (IDF's default
minimum is 3.1), 400MHz as required by this IDF's production-silicon Kconfig.
`device-es.yaml`: pre-rev3 layout, 360MHz. These layouts are not binary compatible.
Check ROM chip revision before choosing. Never force flashing an incompatible image.
No security/eFuse writes, secure boot or flash encryption are configured.

Onboard H7 exposes Ethernet transformer power pairs and 5V/GND for an optional
PoE module. Presence of H7/RJ45 does not establish a populated compliant PD.
Use only the actual module's documented compatible active PoE source. Never test
with an unidentified passive injector. Record module/source models and disconnect
USB for a genuine PoE-only test.
