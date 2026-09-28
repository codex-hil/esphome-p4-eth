#!/usr/bin/env bash
# Read-only inventory. Does NOT open a serial port or reset any board.
set -euo pipefail
date -u --iso-8601=seconds
lsusb
ip -br link
ip -br address
ip route
ip neigh
ls -l /dev/serial/by-id/ /dev/serial/by-path/ 2>/dev/null || true
for port in /dev/ttyACM* /dev/ttyUSB*; do
  [[ -e $port ]] || continue
  echo "PORT $port"
  udevadm info -q property -n "$port" | sed -n '/^ID_/p'
done
