# Guard Core MCP

An [MCP](https://modelcontextprotocol.io) server that lets AI coding agents answer questions about the Guard security ecosystem from the libraries themselves, instead of from memory.

Covers the whole family: the Python trio ([`fastapi-guard`](https://github.com/rennf93/fastapi-guard), [`guard-core`](https://github.com/rennf93/guard-core), [`guard-agent`](https://github.com/rennf93/guard-agent)) by live introspection, and the Go, TypeScript, PHP and Rust engines, their twenty framework adapters, their telemetry agents, and the [`guard-core-app`](https://github.com/rennf93/guard-core-app) SaaS ingestion contract from a verified registry and knowledge corpus.

## Why

Your agent can already read the docs. What it cannot do is tell you that the `redis_failopen` in your config is silently doing nothing because the real field is `redis_fail_open`, or that the flag you are reaching for did not exist until guard-core 3.5.0, or whether a given request would actually be blocked and by which pattern.

This server answers those from the installed package: real pydantic validation, real field metadata, and the real detection engine. It also answers the cross-language questions the libraries cannot answer: which package guards a Gin, Fastify, Laravel or Rocket app, whether it is tagged or still path-dependent, how to wire its telemetry agent, and what response codes the SaaS ingest endpoint returns.

## Install

Install it **into your project's environment**, not as an isolated tool:

```bash
uv add --dev guard-core-mcp
claude mcp add guard-core -- uv run guard-core-mcp
```

`uvx guard-core-mcp` will start, but an isolated environment contains no `guard-core` or `fastapi-guard` for it to introspect, so it can only answer from bundled documentation. Running it inside your own environment is what makes the answers match the versions you actually ship.

## Tools

| Tool | Answers |
|---|---|
| `versions` | Which Guard libraries are installed here, and at what version |
| `validate_config` | Is this config valid, including typo'd keys pydantic silently ignores |
| `config_fields` | What is this setting, what does it default to, does a setting for X exist |
| `search_docs` | Where do the docs cover this |
| `get_doc` | The full text of one documentation page |
| `check_payload` | Would this request be blocked, and by which pattern |
| `ecosystem` | The full registry matrix: 5 languages, engines, adapters, agents, conformance, SaaS contract |
| `adapter_setup` | Install plus a verified minimal integration for one adapter (e.g. `go` + `gin`) |
| `wire_agent` | How to set up the telemetry agent for a language, including the ingestion contract |

The ecosystem tools are pure data, so they work everywhere, with or without the Python libraries installed. Every quick-start snippet is copied verbatim from the sibling repo READMEs, and `release_status` tells you honestly whether a package is `published`, `tagged`, or still `untagged` (source, `main`, or path dependency only).

## Licence

MIT
