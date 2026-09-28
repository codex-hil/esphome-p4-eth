#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
destination=${1:?Usage: scripts/reproduce.sh /absolute/new-checkout}
[[ $destination = /* && ! -e $destination ]] || { echo 'Destination must be new and absolute' >&2; exit 2; }
# Only committed source enters the reproduction.
git clone --no-local "$root" "$destination"
cd "$destination"
cp secrets.example.yaml secrets.yaml
chmod 600 secrets.yaml
mkdir -p logs
HIL_STATE_DIR="$destination/.state/clean" ./scripts/build.sh device.yaml
HIL_STATE_DIR="$destination/.state/clean" ./scripts/esphome --python scripts/verify-build.py \
  .state/clean/build/p4-eth --profile production | tee logs/clean-build-result.json
