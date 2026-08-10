---

title: Release Notes - Guard Core MCP
description: Release notes for Guard Core MCP, detailing new features, improvements, and bug fixes
keywords: release notes, guard core mcp, mcp server, model context protocol
---

Release Notes
=============

___

v0.1.6 (2026-08-10)
-------------------

Unblock make check-all under the mcp 2.x line: pin mcp>=2, isolate semgrep, bump cryptography (v0.1.6)
------------------------------------------------------------------------------------------------------

- **Fixed** - `pyproject.toml` now declares `mcp>=2` rather than `mcp` unpinned. A blanket `uv lock --upgrade` previously downgraded `mcp` from 2.0.0 to 1.23.3, which removes `mcp.server.mcpserver.MCPServer` and breaks the server at import with `ModuleNotFoundError: No module named 'mcp.server.mcpserver'`. The lower bound stops the resolver from ever selecting a 1.x release. No runtime behaviour change for any environment already on mcp 2.x.
- **Fixed** - `make analysis` stopped working under mcp 2.x. semgrep imports `mcp.server.fastmcp` at CLI startup, a module mcp 2.0.0 removed, so `uv run semgrep` crashed with `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` before scanning anything; semgrep also pins `mcp==1.23.3` in its own metadata, which cannot coexist with this server's `mcp>=2` in one virtualenv. semgrep is now invoked through `uvx --from semgrep` in an isolated environment that resolves its own mcp 1.23.3, and it has been removed from the project dev dependencies so the lock no longer carries the conflicting pin. The commented pre-commit hook was updated to the same `uvx` invocation. semgrep's one audit finding on `config.py` (`importlib.import_module` of a dynamic module name) is a false positive: `module_name` is one of three hardcoded `PACKAGE_MODELS` allowlist entries, not caller-controlled, so no arbitrary module can be loaded. It is suppressed with a `# nosemgrep` annotation and a one-line reason, so `make analysis` now prints no findings.
- **Security** - `cryptography` bumped from 49.0.0 to 50.0.0 to clear PYSEC-2026-3552, which pip-audit flagged and which failed `make security`. The upgrade is targeted (`uv lock --upgrade-package cryptography`); mcp and all other dependencies are unchanged. `cryptography` is a transitive dependency, so no guard-core-mcp source or runtime dependency declaration changed.
- **Changed** - `uv.lock` refreshed so its recorded constraint matches `mcp>=2`, semgrep and its transitive dependencies are no longer recorded, and `cryptography` is bumped to 50.0.0. The resolved version of mcp is unchanged at 2.0.0.

___

v0.1.5 (2026-08-09)
-------------------

Documentation accuracy sweep, corrected tool descriptions, and vendored docs re-synced to the 3.11.0 line (v0.1.5)
------------------------------------------------------------------------------------------------------------------

- **Fixed** - Three tool descriptions did not match their implementations. `config_fields` did not mention that `exact` and `matches` are populated together rather than exclusively, and omitted the `required` key it returns for every field. `check_payload` did not mention that it forces `enable_redis` off regardless of what the caller passes. `versions` did not mention that it also reports the server's own version. A tool's description is what a model reads before deciding to call it, so a wrong description is a functional defect rather than a cosmetic one.
- **Fixed** - `search_docs` silently returns an empty result set for an unrecognized `package`, while `validate_config` and `config_fields` raise a clear error for the same mistake. An agent that typo'd a package name concluded the documentation covered nothing on the topic. The behaviour is unchanged, but the docstring now states it, and [Tools](https://rennf93.github.io/guard-core-mcp/latest/tools/) documents the difference between the four `package`-taking tools.
- **Fixed** - The `versions` example in the installation guide and tool reference showed invented numbers that no real call would produce, and the surrounding prose did not explain what `installed` and `docs_bundled_for` each mean. Both now show real output, and the prose explains that the two are independent, that either side trailing the other is normal, and that a `null` under `installed` is the actual warning sign.
- **Changed** - Vendored `_docs` re-synced from the sibling repos: guard-core 3.11.0, fastapi-guard 7.5.1, guard-agent 2.8.1. This picks up guard-core's ten newly reachable `agent_*` configuration fields and the `on_error` forwarding fix, fastapi-guard's corrected agent buffer guidance, and guard-agent's corrected middleware attachment examples.
- **Changed** - `uv.lock` refreshed so the development environment resolves the current guard-core, fastapi-guard and guard-agent releases rather than three versions behind. `pyproject.toml` dependencies remain unpinned. Note that a blanket `uv lock --upgrade` downgrades `mcp` from 2.0.0 to 1.23.3, which removes `mcp.server.mcpserver.MCPServer` and breaks the server at import; the guard packages were upgraded individually instead.
- No runtime behaviour change. The only source change is docstring text.

___

v0.1.4 (2026-08-09)
-------------------

Sync vendored docs to guard-core 3.10.0 and fastapi-guard 7.5.0 (v0.1.4)
---------------------------------------------------------------------------

- **Changed** - Vendored `_docs` re-synced from the sibling repos: guard-core 3.10.0, fastapi-guard 7.5.0, guard-agent 2.8.0. The `search_docs` and `get_doc` tools now surface guard-core's config-derived security pipeline (`SecurityCheck.applies_to`, which lets a deployment build only the checks its configuration can actually trigger), the new `redis`, `cloud` and `geo` install extras, and the corrected `muted_check_logs` description in the telemetry architecture page.
- **Changed** - fastapi-guard's vendored pages pick up the decorator adoption that makes per-route configuration visible when the pipeline is built, and the shared-state registry's compound `(id(config), id(guard_decorator))` key, which stops two middleware instances sharing one `SecurityConfig` from also sharing a pipeline built under different route visibility.
- **Changed** - `uv.lock` regenerated so the recorded package version matches `pyproject.toml`. `pyproject.toml` dependencies remain unpinned.
- No runtime code or behavior change. Runtime dependencies (`mcp`, `pydantic`) are unchanged and the server does not depend on guard-core at runtime, so this release only refreshes the embedded documentation.

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
