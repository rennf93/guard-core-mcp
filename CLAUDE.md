# AGENTS.md

Guidance for AI agents (including Claude Code) working in this repository.

## Project Overview

Guard Core MCP is an MCP server that answers Guard-ecosystem questions from the **libraries actually installed in the interpreter running it**, not from model memory. It provides config validation, config-field lookup, docs search, and live threat detection for the Guard security libraries.

- **PyPI Package**: `guard-core-mcp`
- **Import Name**: `guard_core_mcp`
- **Console Script**: `guard-core-mcp` (runs `guard_core_mcp.server:main`, stdio transport)
- **Python Support**: 3.10, 3.11, 3.12, 3.13, 3.14
- **Package Manager**: uv
- **Build System**: Docker + Make

That is why the README pushes `uv add --dev guard-core-mcp` over `uvx`: an isolated environment has no Guard libraries to introspect, so `uvx guard-core-mcp` starts but can only answer from bundled documentation.

## Covered Libraries

`PACKAGE_MODELS` (in `guard_core_mcp/config.py`) is the allowlist of packages the server can introspect. Current entries:

| Package | Introspected module | Model class |
|---------|--------------------|-------------|
| `guard-core` | `guard_core` | `SecurityConfig` |
| `fastapi-guard` | `guard` | `SecurityConfig` |
| `guard-agent` | `guard_agent` | `AgentConfig` |

Supporting another package means adding an entry to that dict. The dynamic `importlib.import_module` is safe precisely because it is constrained to this allowlist (hence the `# nosemgrep` on the import line).

## Tools

Each tool is a thin `@mcp.tool()` wrapper in `server.py` around a module function; it converts `ModuleNotFoundError` into `missing_library_error()`'s `{"error", "hint"}` dict. Tools return error dicts; they do not raise. The docstring on each tool is the model-facing contract and carries the caveats (for example, `check_payload` documents that it runs the detection stage only, not the whole middleware pipeline).

| Tool | Signature | What it does |
|------|-----------|--------------|
| `versions` | `versions()` | Reports `installed` versions (live introspection) and `docs_bundled_for` (vendored snapshot) so a caller can detect skew before trusting a docs answer |
| `validate_config` | `validate_config(config, package)` | Validates a config dict against the installed Pydantic model; reports *unknown* keys with `difflib` suggestions (pydantic silently drops them) and captures `DeprecationWarning`s (`_retry_without_rejected_fields` re-validates remaining valid fields so one type error does not hide the rest) |
| `config_fields` | `config_fields(query, package="fastapi-guard")` | Field lookup over the installed model's schema |
| `search_docs` | `search_docs(...)` | Token-count search over the vendored docs corpus |
| `get_doc` | `get_doc(package, path)` | Returns a vendored doc; guards traversal via `resolve()` + `is_relative_to` |
| `check_payload` | `check_payload(payload, config)` (async) | Runs guard-core's real detection engine against a payload via `_SyntheticRequest` |

## Architecture

Two independent answer sources, and the distinction drives most of the design:

- **Live introspection** (`config.py`, `detection.py`) reads the installed pydantic models and calls guard-core's real detection engine. Accurate for whatever version is installed; unavailable if the library is not.
- **Vendored docs snapshot** (`docs.py` + `guard_core_mcp/_docs/`) ships with the package and always works, but is pinned to whatever version was last synced.

**`config.py` and `PACKAGE_MODELS`.** The dict maps package name to `(import module, model class)`. `validate_config` earns its keep by reporting unknown keys with `difflib` suggestions and by capturing deprecation warnings.

**`detection.py` and `_SyntheticRequest`.** That class structurally implements guard-core's `GuardRequest` protocol (no inheritance). If upstream adds a protocol member, this class must gain it or mypy fails on the `request: GuardRequest` assignment. `enable_redis` is forced to `False` so the sandbox never touches Redis, regardless of the caller's config.

**`docs.py` / `guard_core_mcp/_docs/`** is generated output; never hand-edit it. `scripts/sync_docs.py` copies `*.md` from sibling clones at `../fastapi-guard`, `../guard-core`, `../guard-agent` and records each repo's `pyproject.toml` version into `manifest.json`. `make sync-docs` and `make check-docs-drift` therefore require those clones next to this repo; CI's `docs-drift` job clones them itself and runs weekly on a timer, because upstream releases independently of this repo. Search is a naive per-line token count with no index; `get_doc` guards path traversal via `resolve()` + `is_relative_to`.

**`server.py` is a thin tool layer.** Keep new tools in that shape, and keep the real logic in the module rather than the tool body.

## Quick Start

```bash
# In the project that has the Guard libraries installed:
uv add --dev guard-core-mcp
claude mcp add guard-core -- uv run guard-core-mcp
```

`uvx guard-core-mcp` will start, but an isolated environment contains no `guard-core` or `fastapi-guard` for it to introspect, so it can only answer from bundled documentation. Running it inside your own environment is what makes the answers match the versions you actually ship.

## Development Commands

Local (fast, what you want while iterating):

```bash
uv sync --extra dev                          # install
uv run pytest                                # full suite (coverage is in addopts)
uv run pytest -m "not e2e"                   # skip the stdio-subprocess tests
uv run pytest tests/test_config.py::test_name -v   # single test
uv run ruff check --fix . && uv run ruff format .
uv run mypy guard_core_mcp
uv run pre-commit run --all-files            # exactly what CI's pre-commit job runs
```

Makefile (note: `make test`, `make lint` and `make check-all` build and run a Docker image, then `docker system prune -f`; they are the release gates, not the inner loop):

```bash
make test            # default Python 3.10 in Docker; make test-3.11 ... test-3.14
make lint            # ruff + mypy in Docker
make fix             # auto-fix with ruff
make check-all       # lint + security + quality + analysis
make sync-docs       # regenerate guard_core_mcp/_docs from sibling repo clones
make check-docs-drift
make serve-docs      # serve the published MkDocs site locally
make lint-docs       # pymarkdownlnt over the markdown outside the package
make fix-docs
make bump-version VERSION=x.y.z
```

## Testing Guidelines

- pytest runs `asyncio_mode = "auto"`, so async tests need no marker
- The `e2e` marker means the test spawns a real server subprocess over the MCP stdio transport; skip locally with `uv run pytest -m "not e2e"`
- Suite layout: `test_config.py`, `test_detection.py`, `test_docs.py`, `test_server.py`, `test_e2e.py`, `test_sync_docs.py`, `test_sync_docs_script.py`
- Coverage is configured in `addopts`; the Docker `make test` gates releases

### Constraints worth knowing before you edit

- **`mcp>=2` is a hard pin.** The server imports `mcp.server.mcpserver.MCPServer`, which does not exist in mcp 1.x, so a blanket `uv lock --upgrade` that downgrades mcp breaks the server at import. Semgrep pins `mcp==1.23.3`, so it runs via `uvx --from semgrep` rather than as a dev dependency.
- **Complexity ceilings are enforced**, not advisory: xenon `--max-absolute B --max-modules A --max-average A`, plus vulture at `min_confidence = 100`, deptry, and strict mypy (`disallow_untyped_defs`, `warn_unreachable`, and friends). This is why the modules are built from small helpers.
- `.roboco/conventions.yml` blocks lint suppressions and warns on inline comments.
- The version string lives in `pyproject.toml`, `guard_core_mcp/__init__.py`, `.mike.yml`, `docs/versions/versions.json`, `docs/index.md`, `CHANGELOG.md` and `docs/release-notes.md`. Use `make bump-version VERSION=x.y.z` rather than editing by hand.
- `docs/` is the published MkDocs site for this project; `guard_core_mcp/_docs/` is the vendored upstream corpus the server serves. Different things, easy to confuse.

## Best Practices

1. **Always use uv** for package management
2. **Keep tools thin**: logic lives in `config.py` / `detection.py` / `docs.py`, never in the tool body; error dicts, not raises
3. **Never hand-edit `guard_core_mcp/_docs/`**: change upstream repos and run `make sync-docs`
4. **Run the full suite before claiming green**; the e2e stdio tests catch wiring the unit tests cannot
5. **Do not downgrade `mcp`** below 2; check `uv.lock` after upgrades
6. **Keep the tool docstrings current**: they are the model-facing contract
7. **Use `make bump-version`** for version changes; the string lives in seven places

## Related Projects

- **guard-core** - Security engine whose models and detection engine this server introspects: <https://github.com/rennf93/guard-core>
- **fastapi-guard** - FastAPI/Starlette adapter covered by `PACKAGE_MODELS`: <https://github.com/rennf93/fastapi-guard>
- **guard-agent** - Telemetry client covered by `PACKAGE_MODELS`: <https://github.com/rennf93/guard-agent>
- **flaskapi-guard** - Flask extension adapter: <https://github.com/rennf93/flaskapi-guard>
- **djapi-guard** - Django middleware adapter: <https://github.com/rennf93/djapi-guard>
- **tornadoapi-guard** - Tornado handler/middleware adapter: <https://github.com/rennf93/tornadoapi-guard>
- **guard-core-app** - SaaS platform (API, dashboard, playground): <https://github.com/rennf93/guard-core-app>
