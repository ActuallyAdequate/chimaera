{
  description = "A Flake for markdown editing";

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

    # 1. Define your custom neovim package
    customNeovim =
      (nvf.lib.neovimConfiguration {
        inherit pkgs;
        modules = [
          ./.nix/neovim.nix
        ];
      }).neovim;
  in {
    # This allows you to run 'nix build'
    packages.${system}.default = customNeovim;

    # 2. This allows 'nix develop' to work
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [
        customNeovim
        pkgs.imagemagick
      ];

      shellHook = ''
        # Optional: Force this specific nvim to be first in PATH
        # just in case the shell inherited a messy environment
        export PATH="${customNeovim}/bin:$PATH"

        nvim
      '';
    };
  };
}
