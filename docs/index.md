---

title: Guard Core MCP - MCP Server for the Guard Ecosystem
description: MCP server for the Guard ecosystem, config validation, docs search and live threat detection for fastapi-guard, guard-core and guard-agent
keywords: mcp, model context protocol, fastapi-guard, guard-core, guard-agent, ai agents, security
---

Guard Core MCP
==============

[![PyPI version](https://badge.fury.io/py/guard-core-mcp.svg?cache=none&icon=si%3Apython&icon_color=%23008cb4)](https://badge.fury.io/py/guard-core-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`guard-core-mcp` is an [MCP](https://modelcontextprotocol.io) server that lets AI coding agents answer questions about the Guard security ecosystem ([`fastapi-guard`](https://github.com/rennf93/fastapi-guard), [`guard-core`](https://github.com/rennf93/guard-core) and [`guard-agent`](https://github.com/rennf93/guard-agent)) by introspecting the libraries actually installed in your project, instead of answering from training data.

___

Why
---

An agent can already read the docs. What it cannot do from memory is tell you that `redis_failopen` in your config is silently doing nothing because the real field is `redis_fail_open`, that a flag did not exist until guard-core 3.5.0, or whether a given request would actually be blocked and by which pattern. Pydantic ignores unknown keys instead of raising, so a misspelled setting fails silently at runtime with no error anywhere.

`guard-core-mcp` answers those questions from the packages installed in the interpreter running it: real Pydantic model validation, real field metadata pulled from the model itself, and requests run through guard-core's actual detection engine. When a library is not installed, the affected tools say so explicitly instead of guessing, see [Installation](installation.md) for what that looks like.

___

The Six Tools
-------------

| Tool | Answers |
|---|---|
| `versions` | Which Guard libraries are installed here, and at what version, alongside the versions the bundled documentation covers |
| `validate_config` | Is this config dict valid against the real `SecurityConfig`/`AgentConfig` model, including typo'd keys Pydantic would otherwise ignore, and deprecated fields |
| `config_fields` | What does this setting do, what's its type and default, or does a setting for X exist at all |
| `search_docs` | Which bundled documentation page covers this, with a citable live URL |
| `get_doc` | The full text of one bundled documentation page |
| `check_payload` | Would this request be blocked by guard-core's detection engine, and by which pattern |

See [Tools](tools.md) for the signature, parameters, and an example call and response for each.

___

Documentation
-------------

- [Installation](installation.md)
- [Tools](tools.md)
- [Release Notes](release-notes.md)
