# Agentic Engineering Workshop: Software

Welcome, and thanks for joining! We look forward to the workshop with you.
Please complete the setup below beforehand, so we can start right away.

## Setup

We use the package manager **Nix**; `flake.nix` declares all tools.
Nix stores them in `/nix/store`, separate from your other software.
They are only on your `PATH` inside the `nix develop` shell.

1. Install Nix. We recommend the Determinate installer (Linux and macOS, flakes enabled):
   https://docs.determinate.systems/determinate-nix/
   If you use the official installer (https://nixos.org/download/), enable flakes:
   `mkdir -p ~/.config/nix && echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf`
2. In this repo, enter the dev shell: `nix develop`
   This opens a shell with the tools from `flake.nix`. `exit` leaves it.
3. Check it works: `claude --version && sbt --version`

To uninstall Nix later, follow https://manual.determinate.systems/installation/uninstall.html (Determinate installer) or https://nix.dev/manual/nix/stable/installation/uninstall.html (official installer).

### Without Nix

Alternatively, install these yourself:
- git: https://git-scm.com/downloads
- JDK 21 (e.g. Temurin): https://adoptium.net/temurin/releases/?version=21
- sbt: https://www.scala-sbt.org/download/
- scalafmt: https://scalameta.org/scalafmt/docs/installation.html
- just: https://just.systems/man/en/installation.html
- jq: https://jqlang.org/download/
- nono sandbox: https://nono.sh/docs/quickstart
- Claude Code: https://claude.com/product/claude-code (needs an account)
