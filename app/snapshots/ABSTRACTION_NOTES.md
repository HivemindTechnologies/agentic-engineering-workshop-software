# Abstraction notes during outer.v15.M3a–M3d

- Extracted `Todos` ops (`markDone`/`edit`/`remove`/`filter`) as pure `List[Todo] => Either` ahead of CLI I/O.
- Centralized list rendering in `Renderer` (table/json/markdown/yaml) with color as an edge boolean.
- Introduced `AppConfig.resolve` for CLI → env → HOCON → defaults precedence instead of scattering env reads.
- Store encode hand-rolled to avoid null-list YAML redundancy with the derived codec path.
