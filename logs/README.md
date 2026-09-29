# Evidence logs

Raw logs are kept locally and ignored by Git because they can contain LAN details
and device identifiers. Commit reviewed summaries/hashes, not credentials.

Initial preparation markers have been replaced by real logs where tests ran.
`first_boot.log` intentionally preserves the initial PHY-address failure;
`ethernet-boot.log` is the subsequent successful unpatched boot. `power_cycle_test.log`
remains an explicit NOT RUN marker until genuine supply cycles are performed.
Serial-capture refuses to overwrite existing evidence.
Expected: first_boot.log, ethernet.log, ota_test.log, mqtt_test.log,
power_cycle_test.log. Additional local logs cover inventory/build/configuration.
