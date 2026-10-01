# 💡 Files 1

**Files as the Interface.** Chat is a transcript; a file is a contract.
Plan, environment, sandbox and skills become reviewable artifacts: every change is a diff, and a lost session costs nothing.

----

## Plans as files

The plan is declared in `docs/PLAN.md`:

```markdown
# Export user data

Decided:
- CSV, one file per user
- synchronous download, no background job

Open:
- include deleted items?
```

- A changed decision is a diff you review
- You, your colleague and the next session read the same text
- `/compact` and `/clear` leave it as it is

----

## Environments as files

The dev shell is declared in `flake.nix`:

```nix
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  outputs = { nixpkgs, ... }:
    let pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = with pkgs; [ sbt just ];
      };
    };
}
```

- The agent adds a missing tool as a diff you review
- You, your colleague and the agent enter the same shell: `nix develop`
- CI enters it too: `nix develop --command just check`

----

## Sandboxes as files

The boundary is declared in `nono.json`:

```json
{
  "extends": "nolabs-ai/claude",
  "groups": { "include": ["deny_credentials", "deny_shell_history"] },
  "filesystem": { "allow": ["$WORKDIR"] },
  "environment": { "deny_vars": ["SECRET_*"] }
}
```

- Widening the boundary is a diff you review
- You, your colleague and the agent run inside the same walls: `just claude`
- A stricter variant: `nono-strict.json` adds network restrictions and credential providers

----

## Paths as an index

- The agent reads directory names before code
- `exercises/`, `platform/`, `incidents/` beats `misc/`, `stuff/`, `src2/`
- One responsibility per folder
