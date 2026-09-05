Release Notes
=============

___

v1.0.1 (2026-09-05)
-------------------

Vendored docs re-synced to guard-core 4.0.1 (v1.0.1)
----------------------------------------------------

- **Changed** - Vendored `_docs` re-synced to the guard-core 4.0.1 tree: `api/utilities.md` gains the public `redact_blob_for_display` and `redact_url_for_display` helpers with their documented limits, `api/handlers.md` documents `ban_ip` returning a bool that is False when the self-DoS guard refuses a ban, `configuration/detection-tuning.md` states the 40 second reach-probe budget and the host-normalized timing, and the release notes carry the 4.0.1 section. The fastapi-guard corpus picks up the tutorial snippet formatting fix from fastapi-guard PR #134.
- **Changed** - `uv.lock` moves guard-core to 4.0.1.

___

v1.0.0 (2026-09-04)
-------------------

Vendored docs re-synced to guard-core 4.0.0, guard-agent 3.0.0 and fastapi-guard 8.0.0 (v1.0.0)
-----------------------------------------------------------------------------------------------

- **Changed** - Vendored `_docs` re-synced from the sibling repos at the trees that ship as guard-core 4.0.0, guard-agent 3.0.0 and fastapi-guard 8.0.0. The guard-core corpus now describes grammar-based secret redaction across every log line, telemetry event, on_block payload, span, metric and Redis key name, the per-context detection matrix with every disclosed miss and false positive named, the single telemetry contract (`pattern_matched`, `metadata.category`, `handler_name`, decorator events through the bus), the `log_sensitive_headers`, `log_sensitive_params` and `log_sensitive_body_fields` knobs, the deprecation of unconfigured (legacy) detection, and the breaking changes an operator must read before upgrading: `excluded_detection_headers` no longer silences a header, `require_headers` enforces non-sentinel values, the endpoint rate-limit Redis key hashes the path segment, `detect_pattern_match` returns a redacted pattern source, and `SecurityConfig` validation errors no longer echo the rejected input value (so `validate_config` answers name the field and the reason without the value). The guard-agent corpus describes header sanitisation at ingest and egress, the buffer that no longer loses events on a failed send, overflow or cancellation, and the async requeue protocol; the fastapi-guard corpus describes the 8.0.0 lockstep.
- **Changed** - Version 1.0.0: the major follows the guard-core 4.0.0, guard-agent 3.0.0 and fastapi-guard 8.0.0 majors this server documents. The `uv.lock` bump to those releases and the re-captured `versions` examples land once the three packages are on PyPI.

___

v0.1.12 (2026-09-01)
--------------------

Vendored docs re-synced to guard-core 3.17.0 and guard-agent 2.10.0, both locked (v0.1.12)
------------------------------------------------------------------------------------------

- **Changed** - Vendored `_docs` re-synced from the sibling repos: guard-core 3.17.0, guard-agent 2.10.0, fastapi-guard 7.8.2 (unchanged). This picks up guard-core 3.17.0's release-notes entry: dynamic rules now persist a last-known snapshot on every successful apply (Redis whenever a redis handler is present, plus an opt-in JSON file behind the new `dynamic_rules_cache_path` field) and hydrate it once at startup before the update loop starts, so a process restarted during a SaaS outage comes up with the last applied rules instead of base config; expired, malformed, or newer-schema snapshots are discarded with an error logged. The sync also carries the matching `dynamic_rules_cache_path` row in the vendored `configuration/security-config.md` reference, and guard-agent 2.10.0's release-notes entry: every `guard_agent` log line now carries an origin prefix (`[guard_agent.client] ...`), `setup_agent_logging` gained a JSON format and optional file sink, and the automatic setup run by the handler constructors is non-destructive to host logging configuration.
- **Changed** - `uv.lock` now resolves guard-core 3.17.0 and guard-agent 2.10.0 from PyPI (`uv lock --refresh --upgrade-package guard-core --upgrade-package guard-agent`; `--refresh` mattered again, the uv index lagged the fresh guard-core publish by a minute). No other dependency, including `mcp`, moved. No behavior changes to the server itself: `dynamic_rules_cache_path` is a new optional `SecurityConfig` field, so `validate_config` accepts it as a known field out of the box, and guard-core 3.17.0 introduces no new construction-time warnings for `validate_config` to surface. The worked `versions` examples in the docs are re-captured from this build.
- **Changed** - guard-core 3.17.0 also un-deprecated `ipinfo_token` and `ipinfo_db_path`: they were never meant to be deprecated. `validate_config`'s `deprecated` report no longer carries an entry for either field, where a 0.1.11 install reported one for `ipinfo_token` (and would have for `ipinfo_db_path`) on the same config. This is the one user-visible change to `validate_config`'s output in this release.
- **Changed** - pytest now runs with `filterwarnings = ["error"]`, so any warning fails the suite instead of passing silently.

___

v0.1.11 (2026-09-01)
--------------------

Vendored docs re-synced to guard-core 3.16.0, guard-core locked at 3.16.0 (v0.1.11)
-----------------------------------------------------------------------------------

- **Changed** - Vendored `_docs` re-synced from the sibling repos: guard-core 3.16.0, fastapi-guard 7.8.2 (unchanged), guard-agent docs bundle 2.9.1 (unchanged). This picks up guard-core 3.16.0's release-notes entry: the new optional `SecurityConfig.on_block` callback fired exactly once per blocked or passively flagged request, and the TTLCache check-then-use closures on the security-headers, IP-ban and dedup cache reads that previously raised `KeyError` at a TTL boundary and failed the ban check open. The sync also carries the matching `on_block` row in the vendored `configuration/security-config.md` reference.
- **Changed** - `uv.lock` now resolves guard-core 3.16.0 from PyPI (`uv lock --upgrade-package guard-core`). No other dependency, including `mcp`, moved. No behavior changes to the server itself: `on_block` is a new optional `SecurityConfig` field, so `validate_config` accepts it as a known field out of the box, and guard-core 3.16.0 introduces no new construction-time warnings for `validate_config` to surface.

___

v0.1.10 (2026-08-27)
--------------------

Vendored docs re-synced to guard-core 3.15.0 / fastapi-guard 7.8.2, and check_payload now reflects guard-core 3.15.0's auto-configuring detection singleton (v0.1.10)
---------------------------------------------------------------------------------------------------------------------------------------------------------------------

- **Changed** - Vendored `_docs` re-synced from the sibling repos: guard-core 3.15.0, fastapi-guard 7.8.2, guard-agent 2.9.0 (unchanged). This picks up guard-core 3.15.0's post-3.14.0 follow-ups: the rate limiter now honors `redis_fail_open` on a Redis failure instead of always falling back to the in-memory window (breaking when `redis_fail_open=False`, the default: a Redis outage now raises `GuardRedisError` and lets `fail_secure` decide, rather than silently falling back); a new `detection_max_json_depth` (default 32) bounds how deep a JSON body is walked structurally and a new `detection_max_scan_chars` (default 65536) bounds the total characters scanned per request, alongside the existing `detection_max_scan_values`; `SecurityConfig` now warns at construction when `whitelist` contains a `/0` network, mirroring the existing `trusted_proxies` warning; a declared `trusted_proxy_depth` that over-counts the real proxy hops is now corrected by walking the `X-Forwarded-For` chain right to left instead of silently trusting a client-rotatable entry; a body whose declared `Content-Length` exceeds `detection_max_body_inspect_bytes` is now read and scanned through the adapter's bounded reader instead of skipped outright; and `setup_custom_logging` no longer double-logs into a host's own root logger handlers. And fastapi-guard 7.8.2's lockstep: `StarletteGuardRequest.url_path` and the websocket adapter's equivalent now resolve the route-relative path under an ASGI `root_path` or a mounted sub-app instead of the full mount-prefixed path, so `exclude_paths` and `endpoint_rate_limits` keys match correctly under a mount; this also picks up 7.8.1's `make_guard_websocket` factory, close-code constants, and Redis-manager fixes for the websocket guard.
- **Fixed** - `check_payload`'s docstring described guard-core 3.14.0's `detection_max_scan_values` cap alone; it now also documents 3.15.0's `detection_max_scan_chars` (default 65536) and `detection_max_json_depth` (default 32) caps, and the fact that `detect_penetration_attempt` now configures guard-core's detection singleton from the config it receives. `check_payload` never configured that singleton itself, so every prior release of this tool ran guard-core's slower legacy pattern-matching path instead of the enhanced path a real adapter runs, and could report a different verdict than a live request would for the same payload. 0.1.10 is the first release where `check_payload`'s verdicts come from that same enhanced path. `validate_config`'s docstring also now names the new `whitelist` `/0` construction warning alongside the existing `trusted_proxies` one.
- **Changed** - `uv.lock` now resolves guard-core 3.15.0 and fastapi-guard 7.8.2 from PyPI (`uv lock --refresh --upgrade-package guard-core --upgrade-package fastapi-guard`; `--refresh` mattered here since the uv package index lagged a few minutes behind the fresh PyPI publish). No other dependency, including `mcp`, moved.

___

v0.1.9 (2026-08-26)
-------------------

Vendored docs re-synced to guard-core 3.14.0 / fastapi-guard 7.8.0, and validate_config now surfaces guard-core's construction-time warnings (v0.1.9)
-----------------------------------------------------------------------------------------------------------------------------------------------------

- **Changed** - Vendored `_docs` re-synced from the sibling repos: guard-core 3.14.0, fastapi-guard 7.8.0, guard-agent 2.9.0 (unchanged). This picks up guard-core 3.14.0's post-3.13.0 hardening pass: `SecurityConfig` now warns at construction on a `trusted_proxies` `/0` network (`0.0.0.0/0`, `::/0`) and on an empty `enabled_detection_categories` with detection enabled; a request with no client address is now rejected instead of skipping the entire security pipeline, with a new `unix` `trusted_proxies` token for Unix-socket deployments; `X-Forwarded-For` chain warnings for a depth that cannot be satisfied or that resolves to another trusted proxy; rate-limit and behavior-tracker in-memory stores are now LRU-bounded at 10,000 clients; `detection_max_scan_values` bounds the number of request values scanned per request (default 512); ban address canonicalization closes a silent no-op between IP spellings; and GeoIP, Redis-outage-at-startup and Azure cloud-IP-range resilience fixes. And fastapi-guard 7.8.0's lockstep for the same guard-core release: repeated `X-Forwarded-For` header lines are now joined before guard-core resolves the client, a `guard_websocket` dependency closes the gap where `SecurityMiddleware` never ran for WebSocket scopes, and a Redis outage at startup now returns a clean 503 instead of crashing.
- **Fixed** - `validate_config` only captured `warnings.warn` records (`DeprecationWarning`), missing guard-core's `logger.warning` signals for its own construction-time misconfiguration checks: an unknown constructor keyword, the 3.14.0 `trusted_proxies` `/0` warning, and the empty `enabled_detection_categories` warning. A temporary `logging.Handler` is now attached to the `guard_core` logger for the duration of `SecurityConfig` construction, and its deduplicated records are reported under a new `construction_warnings` field; the logger's original handlers and level are always restored afterward. The `validate_config` and `check_payload` tool docstrings now document this and guard-core 3.14.0's `detection_max_scan_values` request-value scan cap (default 512, names and values counted; a payload beyond it gets a verdict on the scanned prefix only).
- **Changed** - `uv.lock` is deliberately untouched. guard-core 3.14.0 and fastapi-guard 7.8.0 are not yet published to PyPI, so `uv lock` cannot resolve them, and a blanket `uv lock --upgrade` would still downgrade `mcp`. Run `uv lock --upgrade-package guard-core --upgrade-package fastapi-guard` once both are published.

___

v0.1.8 (2026-08-25)
-------------------

Vendored docs re-synced to the guard-core 3.13.0 / fastapi-guard 7.7.0 / guard-agent 2.9.0 line, and worked examples refreshed (v0.1.8)
---------------------------------------------------------------------------------------------------------------------------------------

- **Changed** - Vendored `_docs` re-synced from the sibling repos: guard-core 3.13.0, fastapi-guard 7.7.0, guard-agent 2.9.0. This picks up guard-core 3.13.0's auth-verifier machinery (`require_auth` and `api_key_auth` now require a resolvable verifier and fail-closed 401 without one; `require_authorization_header` is the presence-only escape hatch; the approved principal lands on `request.state.auth_principal`), the new `threat_ban_config` per-category ban-thresholds field and the `enable_rate_limit_auto_ban` flag that feeds rate-limit violations into the penetration-detection auto-ban engine, and the `check_ip_access` / `check_rate_limit_by_ip` / `is_ip_allowed` helpers re-exported in `guard_core.__all__`; fastapi-guard 7.7.0's auth-verifier lockstep for the same guard-core release; and guard-agent 2.9.0 carrying `guard_core_version` on its telemetry.
- **Changed** - `uv.lock` and the development environment refreshed to resolve guard-core 3.13.0, fastapi-guard 7.7.0 and guard-agent 2.9.0. Each package was upgraded individually (`uv lock --upgrade-package`, with `--no-cache` for guard-agent while PyPI propagation caught up after its publish) rather than via a blanket `uv lock --upgrade`, which still downgrades `mcp` from 2.0.0 to 1.23.3 and breaks the server at import. `mcp` stays at 2.0.0; `pyproject.toml` runtime dependencies remain unpinned and unchanged.
- **Fixed** - The worked examples in the installation guide and tool reference were frozen at the 0.1.7 line (guard-core 3.12.0, fastapi-guard 7.6.0, guard-agent 2.8.1). All five example blocks now show real, live output captured against the installed 3.13.0 / 7.7.0 / 2.9.0 line: `versions()` reports `guard_core_mcp` 0.1.8 and the new installed and bundled versions; the `validate_config` typo example's `did_you_mean` now lists two suggestions (`enable_rate_limiting` and the new `enable_rate_limit_auto_ban`) where it previously listed one; the `config_fields` example's `matches` now includes `threat_ban_config` and `enable_rate_limit_auto_ban`, which both mention `rate_limit` and so surface for that query for the first time; and the `search_docs` example's second-result score moved from 79 to 80 as fastapi-guard's release notes grew.

___

v0.1.7 (2026-08-15)
-------------------

check_payload body-scan fix for guard-core 3.12.0, documentation accuracy sweep, and vendored docs re-synced to the 3.12.0 line (v0.1.7)
----------------------------------------------------------------------------------------------------------------------------------------

- **Fixed** - Every worked example in the installation guide and tool reference still showed the versions frozen at the 0.1.5 sweep: `versions()`'s own `guard_core_mcp` field showed `0.1.5` although the server had since moved to 0.1.6, and `installed`/`docs_bundled_for` still showed guard-core 3.11.0 and fastapi-guard 7.5.1 despite the sibling repos having released 3.12.0 and 7.6.0. The `version` field in both `validate_config` examples and the `config_fields` example carried the same stale 7.5.1, and the `search_docs` example's second result score was stale at 76 now that fastapi-guard's growing release notes push it to 79. All five example blocks now show real, live output captured against the installed 3.12.0/7.6.0/2.8.1 line.
- **Fixed** - `config_fields`'s tool docstring said `matches` lists every field "whose name or description contains the query", which is not what the implementation does: it splits the query into words and requires every word to appear somewhere in the combined name and description, independent of order or adjacency. `config_fields("limit rate", ...)` matches `rate_limit` even though the literal substring "limit rate" appears nowhere in its name or description. The docstring now says "contains every word of the query (case-insensitively, word order does not matter)", matching what [Tools](https://rennf93.github.io/guard-core-mcp/latest/tools/) already documented correctly.
- **Fixed** - `pyproject.toml`'s package description used an em dash between the product name and its feature list; replaced with a plain hyphen.
- **Changed** - Vendored `_docs` re-synced from the sibling repos: guard-core 3.12.0, fastapi-guard 7.6.0, guard-agent 2.8.1 (unchanged). This picks up guard-core's exclusion-path enforcement fix (an excluded path now still enforces IP bans, blacklists, blocked countries, blocked cloud providers and rate limits; only detection and behavioral tracking are skipped there), the identity-block escalation fix so a route-level IP block is no longer bypassed by a stale global-whitelist flag left over from the earlier global check, and fastapi-guard's bounded body reading for chunked requests plus working response-body `return_pattern` rules.
- **Changed** - `uv.lock` and the development environment refreshed to resolve guard-core 3.12.0 and fastapi-guard 7.6.0; `guard-agent` was already current at 2.8.1. Upgraded individually rather than via a blanket `uv lock --upgrade`, which still downgrades `mcp` from 2.0.0 to 1.23.3 and breaks the server at import. `pyproject.toml` runtime dependencies remain unpinned and unchanged.
- **Fixed** - `check_payload`'s sandbox request was not compliant with guard-core 3.12.0's body-read contract, so the detection stage silently skipped the request body. guard-core 3.12.0's `detect_penetration_attempt` reads `content-length` to decide whether to scan the body and caches the capped body on `request.state`; the synthetic request carried no `content-length` header and returned `None` for `state`, so detection took the no-content-length branch and never inspected the body, and the body-cache path would have raised `AttributeError` if reached. The synthetic request now injects a `content-length` header when a body is present and exposes a mutable `state` namespace, so the detection tool actually inspects the request body against guard-core 3.12.0. This is a runtime behaviour change for `check_payload` (the body was not scanned before), not a documentation change.

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
------------------------------------------------------------------------

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
---------------------

- **Changed** — `mcp` is declared without a version bound again, matching how every other dependency in the Guard ecosystem is declared. Installs resolve the latest SDK, which is what the server targets.

___

v0.1.1 (2026-07-28)
-------------------

MCP SDK 2.0 compatibility (v0.1.1)
----------------------------------

- **Fixed** — The server failed to start against `mcp` 2.0.0 with `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`. The SDK renamed `FastMCP` to `MCPServer` and moved it to `mcp.server.mcpserver`; `guard-core-mcp` now imports it from there.
- **Changed** — `mcp` is now required at `>=2`, since the pre-2.0 import path no longer exists.

___

v0.1.0 (2026-07-25)
-------------------

Config, documentation and detection tools (v0.1.0)
--------------------------------------------------

- **Added** — `validate_config` — validates a config dict against the real Pydantic `SecurityConfig` / `AgentConfig` model for `fastapi-guard`, `guard-core`, or `guard-agent`, reporting unknown keys (with typo suggestions), validation errors, and deprecation warnings.
- **Added** — `config_fields` — looks up a config field by exact name or fuzzy query, returning its type, default, required-ness, and description straight from the installed Pydantic model.
- **Added** — Bundled documentation for `fastapi-guard`, `guard-core`, and `guard-agent` (95 vendored pages, kept in sync via `scripts/sync_docs.py`), plus `search_docs` and `get_doc` to query it.
- **Added** — `check_payload` — runs a request through guard-core's real detection engine in a Redis-disabled sandbox, reporting whether it would be blocked and by which pattern.
- **Added** — Repo scaffolding matching the rest of the Guard ecosystem: community files, pre-commit and CI tooling configuration, and packaging metadata.

___

v0.0.1 (2026-07-25)
-------------------

Name reservation (v0.0.1)
-------------------------

- **Added** — Initial scaffold published to PyPI to reserve the `guard-core-mcp` name. Only the `versions` tool — reporting which Guard libraries are installed and at what version — is implemented.

___
