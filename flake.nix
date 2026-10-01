{
  description = "todo-list-cli tooling: JDK, sbt, formatter, just, nono, Claude Code";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = {nixpkgs, ...}: let
    systems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];
    forEachSystem = f:
      nixpkgs.lib.genAttrs systems (system:
        f (import nixpkgs {
          inherit system;
          config.allowUnfreePredicate = pkg: nixpkgs.lib.getName pkg == "claude-code";
        }));
  in {
    devShells = forEachSystem (pkgs: {
      default = pkgs.mkShellNoCC {
        packages = [
          pkgs.git
          pkgs.jdk21
          pkgs.sbt
          pkgs.scalafmt
          pkgs.just
          pkgs.nono
          pkgs.jq
          pkgs.yq-go
          pkgs.claude-code
        ];
        # Keep sbt and coursier caches out of $HOME. $PWD is where
        # `nix develop` was started, normally the repo root.
        shellHook = ''
          export COURSIER_CACHE=$PWD/.cache/coursier
          export SBT_OPTS="-Dsbt.global.base=$PWD/.cache/sbt"
          "$PWD/scripts/banner" "develop shell"
        '';
      };
    });
  };
}
