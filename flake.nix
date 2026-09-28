{
  description = "Waveshare ESP32-P4-ETH pinned ESPHome toolchain";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/1bc55b9def8165e82073919945c3239903fe4dc2";
  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      python = pkgs.python312.withPackages (p: [
        p.pip p.virtualenv p.setuptools p.wheel
      ]);
      esphome = import ./nix/python-env.nix { inherit pkgs; manifest = ./manifests/nix-python-inputs.json; name = "esphome-hil-python"; };
      idfPython = import ./nix/python-env.nix { inherit pkgs; manifest = ./manifests/nix-idf-python-inputs.json; name = "esphome-idf-python"; };
      idfBundle = import ./nix/idf-bundle.nix { inherit pkgs idfPython; };
    in {
      packages.${system} = { inherit esphome idfPython idfBundle; default = esphome; };
      devShells.${system}.default = pkgs.mkShell {
        packages = [ python esphome pkgs.git pkgs.cmake pkgs.ninja pkgs.gnumake
          pkgs.pkg-config pkgs.gcc pkgs.curl pkgs.cacert pkgs.unzip
          pkgs.zip pkgs.patch pkgs.patchelf pkgs.mosquitto pkgs.iproute2 pkgs.iputils pkgs.usbutils ];
        HIL_ESPHOME = "${esphome}";
        HIL_IDF_BUNDLE = "${idfBundle}";
        HIL_NIX_PYTHON = "${python}/bin/python3";
        HIL_ENVIRONMENT = "nix";
        PYTHONNOUSERSITE = "1";
      };
    };
}
