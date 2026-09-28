#!/usr/bin/env python3
"""Create private credentials without echoing them or overwriting an existing file."""
import base64
import os
from pathlib import Path
import secrets
root = Path(__file__).resolve().parent.parent
value = (root / 'secrets.example.yaml').read_text()
value = value.replace('AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8=', base64.b64encode(secrets.token_bytes(32)).decode())
value = value.replace('ota_password: REPLACE_ME', 'ota_password: ' + secrets.token_urlsafe(32))
value = value.replace('# Public compile-only placeholders. Run scripts/init-secrets.py for real keys.', '# Private. Set broker address and MQTT credentials before flashing.')
fd = os.open(root / 'secrets.yaml', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as f:
    f.write(value)
print('Created secrets.yaml (0600); configure MQTT locally before flashing.')
