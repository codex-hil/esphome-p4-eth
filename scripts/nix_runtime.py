# Imported by the stable script interface after entering a clean Nix shell.
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys


def prepare(root):
    if os.environ.get('HIL_NIX_ACTIVE') != '1' or not sys.base_prefix.startswith('/nix/store/'):
        raise RuntimeError('Nix Python is required; refusing host/private interpreter')
    esphome = Path(os.environ['HIL_ESPHOME'])
    bundle = Path(os.environ['HIL_IDF_BUNDLE'])
    if not all(str(p).startswith('/nix/store/') and p.is_dir() for p in (esphome, bundle)):
        raise RuntimeError('Invalid Nix closure paths')
    state = Path(os.environ.get('HIL_STATE_DIR', str(root/'.state/nix'))).resolve()
    state.mkdir(parents=True, exist_ok=True)
    prefix = state/'idf'
    stamp = state/'nix-bundle.json'
    identity = {'bundle':str(bundle), 'esphome':str(esphome),
                'flake_lock_sha256':hashlib.sha256((root/'flake.lock').read_bytes()).hexdigest()}
    if stamp.exists():
        if json.loads(stamp.read_text()) != identity:
            raise RuntimeError('Nix closure changed; select a fresh HIL_STATE_DIR')
    else:
        if prefix.exists():
            raise RuntimeError('Unidentified IDF state; select a fresh HIL_STATE_DIR')
        shutil.copytree(bundle, prefix, symlinks=True)
        # Only copied framework/state is mutable. Compiler and Python stay in store.
        for path in [prefix, *prefix.rglob('*')]:
            if not path.is_symlink():
                path.chmod(path.stat().st_mode | (0o700 if path.is_dir() else 0o200))
        stamp.write_text(json.dumps(identity, indent=2)+'\n')
    for name in ('home', 'cache', 'data', 'build', 'platformio'):
        (state/name).mkdir(exist_ok=True)
    env = dict(os.environ, HOME=str(state/'home'), XDG_CACHE_HOME=str(state/'cache'),
               ESPHOME_ESP_IDF_PREFIX=str(prefix), ESPHOME_DATA_DIR=str(state/'data'),
               ESPHOME_BUILD_PATH=str(state/'build'), PLATFORMIO_CORE_DIR=str(state/'platformio'),
               PYTHONEXEPATH=os.environ['HIL_NIX_PYTHON'], PYTHONNOUSERSITE='1',
               IDF_CCACHE_ENABLE='0', ESPHOME_CCACHE_ENABLE='0',
               ESPHOME_IDF_DEFAULT_TOOLS='required', ESPHOME_IDF_DEFAULT_TOOLS_FORCE='required',
               PIP_NO_INDEX='1', PIP_DISABLE_PIP_VERSION_CHECK='1',
               HTTP_PROXY='http://127.0.0.1:9', HTTPS_PROXY='http://127.0.0.1:9',
               http_proxy='http://127.0.0.1:9', https_proxy='http://127.0.0.1:9', NO_PROXY='', no_proxy='')
    env.pop('PYTHONPATH', None)
    env['PATH'] = str(esphome/'bin')+os.pathsep+env['PATH']
    return esphome/'bin/esphome', state, env, identity
