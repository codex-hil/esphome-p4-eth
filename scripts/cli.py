"""Pinned Nix ESPHome CLI, with network allowed only for runtime operations."""
from pathlib import Path
import os
import subprocess
import sys
from nix_runtime import prepare
root = Path(__file__).resolve().parent.parent
cli, state, env, identity = prepare(root)
# IDF source/dependencies are supplied by Nix. Runtime API/OTA must reach LAN.
for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy'):
    env.pop(key, None)
args = sys.argv[1:]
if args and args[0] == '--python':
    command = [str(cli.parent / 'python'), *args[1:]]
else:
    command = [str(cli), *args]
raise SystemExit(subprocess.call(command, env=env, cwd=root))
