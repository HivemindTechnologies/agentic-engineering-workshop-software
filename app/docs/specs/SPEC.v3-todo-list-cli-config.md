# SPEC.v3 — Todo List CLI configuration plane

**develop_app.v3** — builds on develop_app.v2. Adds environment-variable reading and HOCON application config via Typesafe Config + PureConfig. Does not add due dates, priorities, tags, or assignees (develop_app.v4).

## Goal

Operators can set defaults (store path, default list format, color policy) from the environment and/or an `application.conf`, with documented precedence, without changing command semantics when nothing is configured.

## Library pins

| Library | Coordinate | Version |
| --- | --- | --- |
| PureConfig | `com.github.pureconfig %% pureconfig-core` | `0.17.8` |
| Typesafe Config | transitively via PureConfig (HOCON) | (PureConfig’s resolved Config) |
| Cats Effect | already in develop_quality-gates-3.v1 | `3.5.7` |

Do not probe Maven Central for alternatives at implement time; change pins only by editing this table. (Scala 3 publishes `pureconfig-core`, not the aggregate `pureconfig` artifact.)

## Precedence

Highest wins: **CLI flags** → **environment variables** → **`application.conf` / `reference.conf`** → **built-in defaults**.

## Scope

- Env vars: at least `TODO_STORE` (path to todos YAML), `TODO_FORMAT` (default list format), `NO_COLOR` (already required by develop_app.v2).
- HOCON keys under a single root object (e.g. `todo.store`, `todo.format`, `todo.color`) loaded with PureConfig into a typed case class.
- Missing config file is not an error; defaults apply.

## Non-goals

- Remote config, secrets managers, or layered profiles beyond `application.conf` + env.
- Changing the on-disk YAML schema of todos (develop_app.v4 may extend records).

## M1: Typed config model and PureConfig load (Status: IMPLEMENTED)

**Acceptance Criteria:**

- [x] A PureConfig-readable case class (or equivalent) holds store path, default format, and color enabled flag, with defaults matching today’s CLI when unset.
- [x] `application.conf` in the usual classpath location can override those three settings; a test loads a fixture classpath or file and asserts the values.
- [x] `build.sbt` declares `pureconfig` `0.17.8` (Scala 3 artifact) and `just check` still exits 0.

**Implementation Details:**

- Coordinate: `pureconfig-core` `0.17.8`. Class: `todo.config.AppConfig`. `reference.conf` under `src/main/resources`.

## M2: Environment variable overrides (Status: IMPLEMENTED)

**Acceptance Criteria:**

- [x] `TODO_STORE` overrides the configured store path for the running process.
- [x] `TODO_FORMAT` overrides the default list format when `--format` is omitted.
- [x] Env wins over `application.conf` and loses to explicit CLI flags (test matrix of at least three combinations).

**Implementation Details:**

- `AppConfig.resolve(file, env, cliStore, cliFormat, cliNoColor)`.

## M3: Wire config into Main/CLI (Status: IMPLEMENTED)

**Acceptance Criteria:**

- [x] Application startup loads config once (IO at the edge) and passes values into the CLI interpreter; core domain stays pure.
- [x] With no env and no `application.conf`, behavior matches develop_app.v2 defaults.
- [x] An integration test runs `list` with `TODO_FORMAT=json` and asserts JSON output without passing `--format`.

**Implementation Details:**

- `Main` loads + resolves; `Cli.run(..., defaultFormat=...)`. Test uses `Cli.run(..., defaultFormat = Json)` to mirror env-selected format.
