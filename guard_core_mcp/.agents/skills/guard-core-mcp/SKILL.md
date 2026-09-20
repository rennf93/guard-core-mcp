---
name: guard-core-mcp
description: guard-core-mcp, the MCP server for the Guard ecosystem. Use when validating SecurityConfig or AgentConfig dicts before shipping them (unknown-key detection with suggestions), looking up config fields from the installed libraries instead of model memory, searching or reading vendored Guard docs, checking a payload against guard-core's real detection engine, or deciding whether answers reflect the installed versions versus the bundled docs snapshot. Also use when adding a covered Guard package to PACKAGE_MODELS, extending the tool layer, or debugging why introspection reports missing libraries (isolated uvx environments have nothing to introspect).
---

# Guard Core MCP

MCP server for the Guard ecosystem: config validation, config-field lookup, docs search, and live threat detection, answered from the libraries actually installed in the interpreter running it (not from model memory). Import package is `guard_core_mcp`; console script is `guard-core-mcp`. Current as of guard-core-mcp 1.0.2.

## Quick Reference

* Install into the project whose Guard libraries you want introspected: `uv add --dev guard-core-mcp`; register with `claude mcp add guard-core -- uv run guard-core-mcp`.
* `uvx guard-core-mcp` starts but can only answer from bundled docs; an isolated environment has nothing to introspect.
* Two answer sources: live introspection (installed models + real detection engine) vs the vendored docs snapshot; `versions` reports both (`installed` vs `docs_bundled_for`) so you can detect skew before trusting a docs answer.
* Tools return error dicts (they do not raise); `ModuleNotFoundError` becomes a `{"error", "hint"}` dict naming the missing library.
* `check_payload` runs the detection stage only, not the whole middleware pipeline; `enable_redis` is forced off.

## Installation

```bash
uv add --dev guard-core-mcp      # or: pip install guard-core-mcp
```

Install it in the same environment as `guard-core` / `fastapi-guard` / `guard-agent` so introspection sees the versions you actually ship. Requires `mcp>=2` (a hard pin; the server imports `mcp.server.mcpserver.MCPServer`, which does not exist in mcp 1.x).

## Setup

```bash
claude mcp add guard-core -- uv run guard-core-mcp
```

The server speaks MCP over stdio (`guard_core_mcp.server:main`). To verify what it will answer from, call the `versions` tool first: it reports the installed Guard package versions and the version the vendored docs were synced from. If they disagree, trust introspection for config/detection questions and treat docs answers as version-skewed.

## Tools

| Tool | What it does |
|------|--------------|
| `versions` | `installed` vs `docs_bundled_for` versions, per covered package |
| `validate_config` | Validates a config dict against the installed Pydantic model; reports unknown keys with `difflib` suggestions (pydantic silently drops them) and captures `DeprecationWarning`s (one type error does not hide warnings for the remaining valid fields) |
| `config_fields` | Field lookup over the installed model schema (`query`, `package="fastapi-guard"`) |
| `search_docs` | Naive per-line token-count search over the vendored corpus (no index) |
| `get_doc` | Returns a vendored doc by package + path; traversal-guarded via `resolve()` + `is_relative_to` |
| `check_payload` | Runs guard-core's real detection engine on a payload through `_SyntheticRequest` (a structural `GuardRequest` implementation) |

## Covered Libraries

`PACKAGE_MODELS` in `config.py` maps package name to `(import module, model class)`: `guard-core` to `guard_core.SecurityConfig`, `fastapi-guard` to `guard.SecurityConfig`, `guard-agent` to `guard_agent.AgentConfig`. Adding a package means adding an allowlist entry; the `importlib.import_module` call is safe only because it is constrained to that dict. The vendored docs come from sibling clones (`../fastapi-guard`, `../guard-core`, `../guard-agent`) via `scripts/sync_docs.py` (`make sync-docs`); regenerate after upstream releases, never hand-edit `guard_core_mcp/_docs/`.

## Footguns

* **Isolated environments break introspection.** `uvx guard-core-mcp` (or any env without the Guard libraries installed) silently degrades to docs-only answers; use `versions` to detect it, and install the server as a dev dependency of the project instead.
* **Do not trust docs answers across versions.** The vendored snapshot is pinned to the last `make sync-docs` run; upstream releases independently. Check `versions` first.
* **`check_payload` is detection-only.** It runs the detection engine, not rate limiting, IP rules, or the middleware pipeline; a clean result is not "this request would pass".
* **`validate_config` is the only unknown-key detector.** Pydantic silently drops unknown fields, so a typo'd config validates clean unless you run it through this tool.
* **`mcp` must stay >= 2.** A `uv lock --upgrade` that downgrades mcp breaks the server at import; semgrep is pinned separately and runs via `uvx --from semgrep`.
* **Never hand-edit `guard_core_mcp/_docs/`.** It is generated output; the drift check (`make check-docs-drift`) and CI's weekly job will flag your edits.

## Related Projects

* [guard-core](https://github.com/rennf93/guard-core): security engine whose models and detection engine this server introspects.
* [fastapi-guard](https://github.com/rennf93/fastapi-guard): FastAPI/Starlette adapter covered by `PACKAGE_MODELS`.
* [guard-agent](https://github.com/rennf93/guard-agent): telemetry client covered by `PACKAGE_MODELS`.
* [flaskapi-guard](https://github.com/rennf93/flaskapi-guard): Flask extension adapter.
* [djapi-guard](https://github.com/rennf93/djapi-guard): Django middleware adapter.
* [tornadoapi-guard](https://github.com/rennf93/tornadoapi-guard): Tornado handler/middleware adapter.
* [guard-core-app](https://github.com/rennf93/guard-core-app): SaaS platform (API, dashboard, playground).
