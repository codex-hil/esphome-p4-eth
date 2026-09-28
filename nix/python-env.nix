{ pkgs, manifest, name }:
let
  py = pkgs.python312;
  bootstrap = py.withPackages (p: [ p.pip p.setuptools p.wheel ]);
  records = (builtins.fromJSON (builtins.readFile manifest)).packages;
  sources = map (r: { inherit (r) filename; source = pkgs.fetchurl { inherit (r) url sha256; }; }) records;
in pkgs.stdenv.mkDerivation {
  pname = name;
  version = "2026-09-24";
  dontUnpack = true;
  nativeBuildInputs = [ bootstrap pkgs.autoPatchelfHook pkgs.makeWrapper ];
  buildInputs = [ pkgs.stdenv.cc.cc.lib pkgs.zlib pkgs.openssl pkgs.libffi pkgs.freetype pkgs.libusb1 ];
  buildPhase = ''
    export HOME=$TMPDIR/home
    mkdir -p "$HOME" inputs
    ${pkgs.lib.concatMapStringsSep "\n" (s: "ln -s ${s.source} inputs/${s.filename}") sources}
    ${bootstrap}/bin/python3 -m venv --without-pip --system-site-packages "$out"
    ${bootstrap}/bin/python3 -m pip --python "$out/bin/python" install \
      --no-index --no-deps --no-build-isolation --no-compile \
      --disable-pip-version-check inputs/*
    "$out/bin/python" -m pip check
    ${pkgs.lib.optionalString (name == "esphome-idf-python") ''
    "$out/bin/python" -c 'import json,sys; from pathlib import Path; (Path(sys.prefix)/".esphome.stamp.json").write_text(json.dumps({"schema_version":"0","features":["core"],"python_version":".".join(map(str,sys.version_info))}))'
    ''}
  '';
  installPhase = "true";
  postFixup = ''
    # Python loads extension modules by dlopen; autoPatchelf handles their ELF deps.
    "$out/bin/python" -c 'import sys; assert sys.base_prefix.startswith("/nix/store/")'
  '';
}
