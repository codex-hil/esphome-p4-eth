# Diagnostic patch — NOT part of the final firmware

`diagnostic-mdio-scan.patch` adds read-only PHY ID register reads after MAC
initialization in ESP-IDF 5.5.5 `components/esp_eth/src/esp_eth.c`. It is not
applied by the normal build. It was temporarily applied only to the disposable
project IDF copy, then fully reverted.

2026-09-29 investigation:

- Baseline address 0: power-up timeout, PHY initialization failed.
- Hypothesis: actual PHY strapping differs from the address inferred from the PDF.
- Read ID registers 2 and 3 at all 32 MDIO addresses after resetting PHY and
  initializing MAC. Only address **1** returned a device: **0243:0c54**.
- All other addresses returned ffff:ffff. Reads succeeded at the bus API level.
- Set `phy_addr: 1` in YAML; remove this diagnostic patch and rebuild.

Raw evidence: `logs/first_boot.log` (failed initial boot),
`logs/mdio-scan-boot.log` (full scan), `logs/ethernet-boot.log` (unpatched retry).
Do not confuse the E log severity used to expose diagnostic reads through IDF's
error-level filter with a failed read; the logged err=0/0 means both reads succeeded.

To reproduce the diagnostic only, apply with `patch -p1` from a disposable IDF
framework root, compile, and flash the diagnostic build. Restore the source or
use a fresh HIL_STATE_DIR before producing final firmware. No pins, OTP or eFuses
are changed by this patch.
