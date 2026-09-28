# Software support audit

Audited installed ESPHome **2026.9.0**, upstream revision
`c6e4c87e525dd343e470d8dea368957a002f6505`, and bundled ESP-IDF **5.5.5**.
Use the pinned Nix closures in this repository; generic upstream documentation
may change after this audit. Python source is packaged by hash in
`manifests/nix-python-inputs.json`; IDF/tool archives are in
`manifests/nix-idf-native-inputs.json`.

- `esp32/__init__.py`: `esp32p4`, separate engineering-sample layout supported;
  native ESP-IDF builder used. Arduino is not used.
- `ethernet/__init__.py`: IP101 accepted for P4; P4 RMII default data pins match
  the Waveshare schematic. MDC/MDIO/reset/clock are explicitly set in YAML.
- `ethernet/ethernet_component_esp32.cpp`: internal EMAC + IP101 IDF driver;
  runtime log reports MAC, IP, speed and duplex. Link/init/DHCP still require hardware.
- IDF `components/esp_eth/src/phy/esp_eth_phy_ip101.c`: checks PHY identity,
  handles reset/negotiation; no custom driver needed for compilation.
- `logger`: UART0 supported; P4 default USB Serial/JTAG would be wrong for the
  CH343-connected Type-C. IDF primary console resolves to UART0.
- Native API encryption, ESPHome OTA with password, MQTT with authentication,
  uptime, ethernet_info, version, debug reset reason and safe_mode are included.
- `Ethernet Connected` is `EthernetComponent::is_connected()` (IP ready), not raw
  cable carrier. PHY link/speed/duplex evidence comes from serial driver logs.
- `web_server` exists but is unnecessary for initial bring-up and is omitted.
- No board-specific ESP32-P4-ETH Ethernet configuration was found in the installed
  component source/local upstream tests. A different Waveshare P4 display model
  is not a configuration for this board.

The prior classic-ESP32 Nix environment supplied the packaging recipe and pinned
Python/IDF inputs. This project changes its compiler to RISC-V using the hash
published in IDF tools.json. It does not inherit classic-ESP32 hardware validation.

Findings during software preparation:

1. Public all-zero API test key is rejected by ESPHome; example now has an explicitly
   public non-zero compile fixture. Generate private keys before flashing.
2. 32MB OTA requests experimental IDF features; using 16MB avoids that requirement.
3. YAML 360MHz on production silicon was silently resolved to 400MHz by IDF Kconfig.
   Use explicit production 400MHz / ES 360MHz and inspect final sdkconfig.
4. IDF production minimum defaults to 3.1; explicitly select 3.0 to avoid rejecting
   a production rev3.0 board. No eFuses are touched by this compile-time selection.

No ESPHome/ESP-IDF source patches or external components are presently required.
This is a source/build finding, not a statement that hardware has passed.
