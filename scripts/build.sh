#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
config=${1:-device.yaml}
stamp=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p logs
./scripts/esphome compile "$config" 2>&1 | tee "logs/build-$stamp.log"
find "${HIL_STATE_DIR:-$root/.state/nix}/build" -name 'firmware*.bin' -type f -exec sha256sum {} + | tee "logs/firmware-$stamp.sha256"
