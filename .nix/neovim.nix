{
  lib,
  pkgs,
  ...
}: let
  words = lib.pipe ./words.txt [builtins.readFile (lib.splitString "\n") (lib.filter (x: x != ""))];
in {
  config.vim = {
    viAlias = false;
    vimAlias = false;
    globals = {
      mapleader = " ";
      maplocalleader = " ";
    };

    theme = {
      enable = true;
      name = "base16";
      base16-colors = {
        base00 = "2B2B2B"; # Background
        base01 = "3B3B3B"; # Lighter Background
        base02 = "545454"; # Selection
        base03 = "707070"; # Comments
        base04 = "A2886A"; # Dark Foreground
        base05 = "E8D0B0"; # Default Text
        base06 = "D2B48C"; # Light Foreground (Tan)
        base07 = "B49770"; # Light Background
        base08 = "DC5C53"; # Variables (Red)
        base09 = "32CD32"; # Numbers (Green)
        base0A = "A52A2A"; # Classes (Brown-Red)
        base0B = "006A00"; # Strings (Deep Green)
        base0C = "8BAE8B"; # Support (Sage)
        base0D = "DC5C53"; # Functions (Red)
        base0E = "FFBFAF"; # Keywords (Salmon)
        base0F = "8B4513"; # Deprecated (Brown)
      };
      transparent = true;
    };

    # Core Utilities
    statusline.lualine.enable = true;
    filetree.neo-tree = {
      enable = true;
      setupOpts.filesystem.filtered_items.visible = true;
    };

    telescope = {
      enable = true;
    };

    terminal.toggleterm = {
      enable = true;
    };

    binds.whichKey.enable = true;

    git.enable = true;

    autocomplete.blink-cmp = {
      enable = true;
      setupOpts = {
        signature.enabled = true;
      };
    };

    clipboard = {
      enable = true;
      providers.wl-copy.enable = true;
      registers = "unnamedplus";
    };

    # Spelling
    spellcheck.enable = true;
    spellcheck.extraSpellWords = {
      # "en_au.utf-8" = words;
      "en.utf-8" = words;
      #"en-AU.utf-16" = words;
    };

    spellcheck.languages = ["en"]; #"en_au"];

    # Images
    utility.images.image-nvim = {
      enable = true;
      setupOpts.backend = "kitty";
      setupOpts.integrations.markdown.clearInInsertMode = true;
      setupOpts.integrations.markdown.enable = true;
      setupOpts.integrations.markdown.filetypes = ["md" "markdown"];
      setupOpts.hijackFilePatterns = ["*.png" "*.jpg" "*.jpeg" "*.gif" "*.webp" "*.svg"];
    };

    # Language
    lsp = {
      enable = true;
      formatOnSave = true;
      inlayHints.enable = true;
      lspkind.enable = true;
    };

    languages = {
      enableTreesitter = true;
      enableFormat = true;

      markdown.enable = true;
      markdown.extensions.markview-nvim.enable = true;
    };

    extraPackages = with pkgs; [gcc nodejs-slim tree-sitter ripgrep fd viu];

    # Keymaps
    keymaps = [
      # File Explorer
      {
        key = "<leader>e";
        mode = "n";
        action = ":Neotree toggle<CR>";
        desc = "Toggle Explorer";
      }
      # Telescope
      {
        key = "<leader>ff";
        mode = "n";
        action = ":Telescope find_files<CR>";
        desc = "Find Files";
      }
      {
        key = "<leader>fw";
        mode = "n";
        action = ":Telescope live_grep<CR>";
        desc = "Live Grep (Words)";
      }
      {
        key = "<leader>fb";
        mode = "n";
        action = ":Telescope buffers<CR>";
        desc = "Find Buffers";
      }
      {
        key = "<leader>fh";
        mode = "n";
        action = ":Telescope help_tags<CR>";
        desc = "Help Tags";
      }
      # Terminal
      {
        key = "<leader>t";
        mode = "n";
        action = ":ToggleTerm<CR>";
        desc = "Toggle Term Floating Terminal";
      }
      {
        key = "<Esc>";
        mode = "t";
        action = "<C-\\><C-n>";
        desc = "Exit Terminal Mode";
      }
      {
        key = "<leader>th";
        mode = "n";
        action = ":ToggleTerm direction=horizontal<CR>";
        desc = "Toggle Horizontal Terminal";
      }
    ];
  };
}
