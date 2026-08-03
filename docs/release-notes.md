---

title: Release Notes - Guard Core MCP
description: Release notes for Guard Core MCP, detailing new features, improvements, and bug fixes
keywords: release notes, guard core mcp, mcp server, model context protocol
---

Release Notes
=============

___

v0.1.3 (2026-08-03)
-------------------

Sync vendored docs to guard-core 3.8.1 + refresh dev deps (v0.1.3)
------------------------------------------------------------------

- **Changed** — Vendored `_docs` re-synced from the sibling repos on master: guard-core 3.8.1, fastapi-guard 7.4.0, guard-agent 2.7.1. The `search_docs` and `get_doc` tools now surface guard-core 3.8.1's release notes (the gated lazy_init warning, the completed preempted-header warning advice, and the global `whitelist_countries` restrict fix) plus the corrected `whitelist_countries` configuration table.
- **Changed** — Development extras in `uv.lock` bumped to match: guard-core 3.5.0 → 3.8.1, fastapi-guard 7.3.0 → 7.4.0, guard-agent 2.7.0 → 2.7.1. `pyproject.toml` dependencies remain unpinned.
- No runtime code or behavior change. Runtime dependencies (`mcp`, `pydantic`) are unchanged and the server does not depend on guard-core at runtime, so this release only refreshes the embedded documentation and the development dependency lockfile.

___

v0.1.2 (2026-07-28)
-------------------

Unpinned mcp (v0.1.2)
--------------------------------------------------------

- **Changed** — `mcp` is declared without a version bound again, matching how every other dependency in the Guard ecosystem is declared. Installs resolve the latest SDK, which is what the server targets.

___

v0.1.1 (2026-07-28)
-------------------

MCP SDK 2.0 compatibility (v0.1.1)
--------------------------------------------------------

- **Fixed** — The server failed to start against `mcp` 2.0.0 with `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`. The SDK renamed `FastMCP` to `MCPServer` and moved it to `mcp.server.mcpserver`; `guard-core-mcp` now imports it from there.
- **Changed** — `mcp` is now required at `>=2`, since the pre-2.0 import path no longer exists.

___

v0.1.0 (2026-07-25)
-------------------

Config, documentation and detection tools (v0.1.0)
--------------------------------------------------------

- **Added** — `validate_config` — validates a config dict against the real Pydantic `SecurityConfig` / `AgentConfig` model for `fastapi-guard`, `guard-core`, or `guard-agent`, reporting unknown keys (with typo suggestions), validation errors, and deprecation warnings.
- **Added** — `config_fields` — looks up a config field by exact name or fuzzy query, returning its type, default, required-ness, and description straight from the installed Pydantic model.
- **Added** — Bundled documentation for `fastapi-guard`, `guard-core`, and `guard-agent` (95 vendored pages, kept in sync via `scripts/sync_docs.py`), plus `search_docs` and `get_doc` to query it.
- **Added** — `check_payload` — runs a request through guard-core's real detection engine in a Redis-disabled sandbox, reporting whether it would be blocked and by which pattern.
- **Added** — Repo scaffolding matching the rest of the Guard ecosystem: community files, pre-commit and CI tooling configuration, and packaging metadata.

___

v0.0.1 (2026-07-25)
-------------------

Name reservation (v0.0.1)
--------------------------

- **Added** — Initial scaffold published to PyPI to reserve the `guard-core-mcp` name. Only the `versions` tool — reporting which Guard libraries are installed and at what version — is implemented.

___
