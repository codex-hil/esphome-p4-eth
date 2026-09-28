{ pkgs, idfPython }:
let
  inputs = builtins.fromJSON (builtins.readFile ../manifests/nix-idf-native-inputs.json);
  framework = pkgs.fetchurl { inherit (inputs.framework) url hash; };
  tool = name: builtins.head (builtins.filter (t: t.name == name) inputs.tools);
  riscv32 = tool "riscv32-esp-elf";
  rom = tool "esp-rom-elfs";
  compiler = pkgs.stdenv.mkDerivation {
    pname = "esphome-riscv32-esp-elf";
    version = riscv32.version;
    src = pkgs.fetchurl { inherit (riscv32) url sha256; };
    nativeBuildInputs = [ pkgs.autoPatchelfHook ];
    buildInputs = [ pkgs.stdenv.cc.cc.lib pkgs.zlib pkgs.expat pkgs.ncurses ];
    dontConfigure = true;
    dontBuild = true;
    dontStrip = true;
    installPhase = ''mkdir -p "$out"; cp -a . "$out/"'';
  };
  romFiles = pkgs.runCommand "esp-rom-elfs-${rom.version}" {} ''
    mkdir -p "$out"
    tar -xzf ${pkgs.fetchurl { inherit (rom) url sha256; }} -C "$out" --strip-components=1
  '';
in pkgs.runCommand "esphome-idf-5.5.5-bundle" {} ''
  mkdir -p "$out/frameworks/5.5.5" "$out/tools/riscv32-esp-elf/${riscv32.version}" "$out/tools/esp-rom-elfs" "$out/penvs"
  tar -xJf ${framework} -C "$out/frameworks/5.5.5" --strip-components=1
  ln -s ${compiler} "$out/tools/riscv32-esp-elf/${riscv32.version}/riscv32-esp-elf"
  ln -s ${romFiles} "$out/tools/esp-rom-elfs/${rom.version}"
  ln -s ${idfPython} "$out/penvs/5.5.5"
  touch "$out/frameworks/5.5.5/.esphome_extracted"
  echo '5.5.5' > "$out/frameworks/5.5.5/version.txt"
  echo '{"schema_version":"0","targets":["esp32p4"],"tools":["required"]}' > "$out/frameworks/5.5.5/.esphome.stamp.json"
  cp ${../manifests/idf-constraints.observed.txt} "$out/espidf.constraints.v5.5.txt"
''
