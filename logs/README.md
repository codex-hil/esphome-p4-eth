# Evidence logs

Raw logs are kept locally and ignored by Git because they can contain LAN details
and device identifiers. Commit reviewed summaries/hashes, not credentials.

The initial five requested logs contain explicit NOT RUN markers until hardware
arrives. They are not captured device output. Archive/remove the marker before
capturing real output; serial-capture refuses to overwrite an existing file.

Expected: first_boot.log, ethernet.log, ota_test.log, mqtt_test.log,
power_cycle_test.log. Additional local logs cover inventory/build/configuration.
