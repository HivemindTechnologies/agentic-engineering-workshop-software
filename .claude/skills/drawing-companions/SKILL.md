---
name: drawing-companions
description: >-
  Interpret or reinterpret Excalidraw drawings into sidecar companion markdown,
  update source checksums, and add curated ideas. Use when the user mentions
  drawings, excalidraw, companion .md, interpret/reinterpret a figure, or asks
  what does this drawing show / what a drawing shows.
---

# /drawing-companions — Interpret, checksum, curate

Pairing (outer.v18.M1): `docs/drawings/<stem>.excalidraw` ↔ `docs/drawings/<stem>.md`.
Exported SVGs under `docs/drawings/output/` are out of scope.

## Contract (do not invent fields)

YAML frontmatter:

| Field | Meaning |
|-------|---------|
| `drawing` | basename, e.g. `hard-easy.excalidraw` |
| `source_sha256` | SHA-256 hex of the drawing file bytes |
| `generated_by` | tool/skill id |
| `generated_at` | UTC timestamp |

Body regions (HTML comments — regenerate only touches **generated**):

```markdown
<!-- generated:begin -->
## Summary
…
<!-- generated:end -->

<!-- curated:begin -->
## Ideas
…
<!-- curated:end -->
```

**Default rule:** reinterpret / refresh updates the generated region and
`source_sha256` / `generated_at` only. Preserve the curated region unless the
user explicitly asks to clear or replace their ideas.

## Deterministic helpers (no Claude required)

```sh
just drawing-companions-status          # board: ok / missing / stale
just drawing-companions-check           # same, exit 1 if missing or stale
just drawing-companions-generate        # stub companions for missing only
scripts/drawing-companions checksum docs/drawings/<stem>.excalidraw
```

`generate-missing` never overwrites an existing companion. Stale means the
recorded `source_sha256` no longer matches the drawing bytes — the prose may be
out of date until you reinterpret.

## Workflow

Copy and track:

```
Drawing companion:
- [ ] 1. Name the drawing path
- [ ] 2. Read drawing (+ companion if present)
- [ ] 3. Write or refresh generated summary
- [ ] 4. Set source_sha256 to current drawing bytes
- [ ] 5. Preserve curated ideas (unless told otherwise)
- [ ] 6. Reinterpret if stale or user asked for a fresh reading
```

### 1. Name the drawing

Resolve to `docs/drawings/<stem>.excalidraw`. Refuse `output/*.svg` as the source.

### 2. Read

Open the `.excalidraw` (and the sidecar `.md` when it exists). If the companion
is missing, create the M1 shape (frontmatter + both regions). Prefer
`just drawing-companions-generate` for bulk stubs, then fill prose here.

### 3–4. Interpret / refresh generated

Describe what the figure shows: labels, structure, the argument it makes.
Update `source_sha256` with:

```sh
scripts/drawing-companions checksum docs/drawings/<stem>.excalidraw
```

Set `generated_by` (e.g. `drawing-companions-skill`) and a fresh `generated_at`.

### 5. Preserve curated ideas

Leave `<!-- curated:begin -->`…`<!-- curated:end -->` intact on reinterpret.
To **add the user’s own ideas**, append under `## Ideas` in that region only —
no full regenerate required.

### 6. Reinterpret

When status says **stale**, or the user wants a fresh reading: rewrite the
generated region, bump checksum + timestamp, keep curated ideas.

## Done when

- Companion path matches the stem
- Frontmatter checksum matches `scripts/drawing-companions checksum`
- Generated summary describes the drawing
- Curated ideas survived unless the user opted to replace them
