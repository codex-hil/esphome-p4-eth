#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
nix_bin=$(command -v nix || true)
if [[ -z $nix_bin && -x /nix/var/nix/profiles/default/bin/nix ]]; then
  nix_bin=/nix/var/nix/profiles/default/bin/nix
fi
[[ -n $nix_bin ]] || { echo 'BLOCKED: Nix is required; no Python fallback' >&2; exit 2; }
[[ -f $root/flake.lock ]] || { echo 'BLOCKED: reviewed flake.lock is required' >&2; exit 2; }
exec "$nix_bin" --extra-experimental-features 'nix-command flakes' develop "$root" \
  --no-write-lock-file --ignore-environment --keep HOME --keep USER --keep HIL_STATE_DIR \
  --command bash -c 'export HIL_NIX_ACTIVE=1; exec "$@"' _ "$@"
