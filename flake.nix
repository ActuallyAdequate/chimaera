{
  description = "A Flake for markdown editing and data processing";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    nvf.url = "github:notashelf/nvf";
  };

  outputs = {
    self,
    nixpkgs,
    nvf,
    ...
  }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};

    # Nix Build Requirements
    buildPython = pkgs.python3.withPackages (ps: with ps; [pandas pandas-stubs pyyaml typing]);

    # Nix Develop Requirements
    customNeovim =
      (nvf.lib.neovimConfiguration {
        inherit pkgs;
        modules = [./.nix/neovim.nix];
      }).neovim;
  in {
    # Nix Build
    packages.${system} = {
      default = pkgs.stdenv.mkDerivation {
        pname = "processed-data";
        version = "1.0.0";
        src = ./.;

        nativeBuildInputs = [buildPython];

        installPhase = ''
          mkdir -p $out
          python3 dev/scripts/process_bodyparts.py \
            core/rules/body-part-list.yaml \
            dev/rules_standards.yaml \
            $out
        '';
      };
    };

    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [
        customNeovim
        pkgs.imagemagick
        buildPython
      ];

      shellHook = ''
        export PATH="${customNeovim}/bin:$PATH"
        echo "Development environment active. Run 'python3 your_script.py' to test manually,"
        echo "or exit and run 'nix build' to generate the final production files."
      '';
    };
  };
}
