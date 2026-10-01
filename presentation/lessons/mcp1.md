# 💡 MCP 1

**Model Context Protocol.** The stack trace sits in Sentry, the ticket in Jira, and you copy both into the chat.
MCP lets the agent read them itself, at a price in context and risk.

----

## What MCP is

A standard plug between the agent and a system it cannot see.

```
Claude Code  ──MCP──▶  Sentry MCP server  ──API──▶  Sentry
(the agent)            (an adapter program)         (the real system)
```

- The **MCP server** is an adapter: it turns one system's API into tools, e.g. `search_issues`
- The agent asks it which tools exist, then calls them; each result lands in the context
- The server runs in one of two ways:
  - **stdio**: a program on your laptop; the agent starts it and talks over stdin/stdout
  - **HTTP**: a URL, usually at the vendor
- Any agent that speaks MCP can use any MCP server

----

## Adding a server

One command per transport:

```sh
# HTTP: Sentry runs the server, you sign in in the browser
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# stdio: claude starts the program, it runs next to the agent
claude mcp add db -- npx -y @bytebase/dbhub@1.3.1 \
  --dsn "postgresql://readonly:pass@localhost:5432/app"
```

In the session, `/mcp` shows whether each server connected and which tools it offers.

----

## What it costs

Everything a server tells the agent lands in the context window, in three steps:

1. **At start**: only tool names, plus the server's instructions
2. **On search**: the agent calls `ToolSearch`, and a matching tool's description and input schema load
3. **On call**: the whole result passes through the model

----

## What it risks

An MCP server is a dependency whose version lives outside your repository.

- Its tool descriptions are text you did not write, and the model follows them as instructions
- **HTTP**: the vendor deploys when it wants; you cannot pin it
- **stdio**: `npx -y pkg` runs whatever npm serves that day; `pkg@1.3.1` pins it in `.mcp.json`

----

## MCP or CLI

**A CLI** where the model knows one: `gh`, `kubectl`, `psql`, or `curl` against an HTTP API

- the model has seen it in training
- it costs nothing until it runs
- its output can be filtered first

**MCP** where the model knows no CLI

- your in-house system: never in training, thinly documented
- `tools/list` tells the agent what exists, each tool with a typed input schema
