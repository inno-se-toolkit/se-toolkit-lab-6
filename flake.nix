{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    devshell = {
      url = "github:deemp/devshell";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.devshell.flakeModule
      ];
      systems = import inputs.systems;
      perSystem =
        { pkgs, ... }:
        let
          python = pkgs.python3.withPackages (ps: [ ps.pydantic ]);
        in
        {
          devshells.default = {
            bash.extra = ''
              export ROOT_DIR="$(pwd)"
            '';
            commandGroups = {
              "1-front-tools" = [
                pkgs.nodejs_25
                pkgs.pnpm
              ];
              "2-back-tools" = [
                pkgs.uv
              ];
              "3-lint-tools" = [
                pkgs.lychee
              ];
              "4-instructors" = [
                {
                  name = "process-meeting-transcript";
                  command = ''
                    ${pkgs.lib.getExe python} ${./instructors/scripts/process-meeting-transcript/process-meeting-transcript.py} "$@"
                  '';
                  help = "Process a meeting transcript directory into speaker-labelled text files";
                }
                {
                  name = "find-broken-links";
                  command = ''
                    ${pkgs.lib.getExe pkgs.lychee} \
                      --include-fragments \
                      --offline \
                      --no-progress \
                      --exclude-path '.venv' \
                      --exclude-path '.direnv' \
                      --exclude-path 'node_modules' \
                      --exclude-path 'tmp' \
                      --root-dir . \
                      --cache \
                      --format json \
                      "$ROOT_DIR"/'**/*.md' \
                      | ${pkgs.lib.getExe python} ${./instructors/scripts/find-broken-links/post-process-lychee.py}
                  '';
                  help = "Find all broken links in all Markdown files (with file:line locations)";
                }
                {
                  name = "lint-docs";
                  command = ''
                    ${pkgs.lib.getExe pkgs.markdownlint-cli2} \
                      '**/*.md' \
                      '#.direnv' \
                      '#.venv' \
                      '#**/node_modules' \
                      '#*/skills' \
                      '#tmp' \
                      '#instructors/{file-reviews,meetings,scripts,lab-plan.md}'
                  '';
                  help = "Lint all Markdown files";
                }
              ];
            };
          };
        };
    };
}
