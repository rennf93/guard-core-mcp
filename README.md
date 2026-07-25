# Guard Core MCP

An [MCP](https://modelcontextprotocol.io) server that lets AI coding agents answer questions
about the Guard security ecosystem from the libraries themselves, instead of from memory.

Covers [`fastapi-guard`](https://github.com/rennf93/fastapi-guard),
[`guard-core`](https://github.com/rennf93/guard-core) and
[`guard-agent`](https://github.com/rennf93/guard-agent).

## Why

Your agent can already read the docs. What it cannot do is tell you that the `redis_failopen`
in your config is silently doing nothing because the real field is `redis_fail_open`, or that
the flag you are reaching for did not exist until guard-core 3.5.0, or whether a given request
would actually be blocked and by which pattern.

This server answers those from the installed package: real pydantic validation, real field
metadata, and the real detection engine.

## Install

Install it **into your project's environment**, not as an isolated tool:

```bash
uv add --dev guard-core-mcp
claude mcp add guard-core -- uv run guard-core-mcp
```

`uvx guard-core-mcp` will start, but an isolated environment contains no `guard-core` or
`fastapi-guard` for it to introspect, so it can only answer from bundled documentation. Running
it inside your own environment is what makes the answers match the versions you actually ship.

## Tools

| Tool | Answers |
|---|---|
| `versions` | Which Guard libraries are installed here, and at what version |
| `validate_config` | Is this config valid — including typo'd keys pydantic silently ignores |
| `config_fields` | What is this setting, what does it default to, does a setting for X exist |
| `search_docs` | Where do the docs cover this |
| `get_doc` | The full text of one documentation page |
| `check_payload` | Would this request be blocked, and by which pattern |

## Licence

MIT
