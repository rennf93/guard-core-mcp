---

title: Installation - Guard Core MCP
description: Install guard-core-mcp into your project's environment and register it with your MCP client
keywords: guard core mcp installation, mcp server setup, claude code mcp
---

Installation
============

Install `guard-core-mcp` **into the same environment as the Guard libraries you use**, as a dev dependency of the project whose `fastapi-guard`, `guard-core` or `guard-agent` config you want the server to introspect:

=== "uv"

    ```bash
    uv add --dev guard-core-mcp
    ```

=== "poetry"

    ```bash
    poetry add --group dev guard-core-mcp
    ```

=== "pip"

    ```bash
    pip install guard-core-mcp
    ```

**Note**: Requires Python 3.10 to 3.14.

___

Register with an MCP client
----------------------------

For Claude Code, run `uv run guard-core-mcp` from the project you just installed it into so the server starts inside that project's virtual environment:

```bash
claude mcp add guard-core -- uv run guard-core-mcp
```

Any MCP-compatible client works the same way: point it at the `guard-core-mcp` console script (`[project.scripts]` registers `guard-core-mcp = guard_core_mcp.server:main`), invoked through whatever runs it inside your project's environment (`uv run`, `poetry run`, or the venv's own `guard-core-mcp` executable) rather than a global or isolated one.

___

Why not `uvx guard-core-mcp`
------------------------------

`uvx guard-core-mcp` will start: the server boots and answers `versions`, `search_docs` and `get_doc` calls fine, because the documentation is vendored inside the wheel itself and needs nothing else installed. But `uvx` runs the package in a fresh, isolated environment built only from `guard-core-mcp`'s own declared dependencies (`mcp`, `pydantic`). It does not contain `fastapi-guard`, `guard-core`, or `guard-agent`, so there is nothing for `validate_config`, `config_fields`, or `check_payload` to introspect.

Calling any of those three tools in an isolated environment returns this instead of an answer:

```json
{
  "error": "guard is not installed in the interpreter running this server",
  "hint": "Install guard-core-mcp into the environment that has your Guard libraries (uv add --dev guard-core-mcp) rather than running it in an isolated one."
}
```

That is the server refusing to guess. The `error` string names the Python **import** name of the missing library, not the PyPI package name (`guard` for `fastapi-guard`, `guard_core` for `guard-core`, `guard_agent` for `guard-agent`), since that is what actually failed to import. `check_payload` always names `guard_core`, the only library its detection sandbox depends on; it has no `package` argument to vary.

The fix is the install flow above: run `guard-core-mcp` in the same environment as the libraries you want it to see, not in an environment `uvx` built just for it.

___

Verifying the install
----------------------

Call `versions` once the server is registered. `installed` reports whatever version of each Guard library is actually resolved in this interpreter, your project's real dependencies. `docs_bundled_for` is unrelated to that: it is fixed at build time to whichever versions `scripts/sync_docs.py` last vendored into this release.

```json
{
  "guard_core_mcp": "0.1.10",
  "installed": {
    "guard-core": "3.15.0",
    "fastapi-guard": "7.8.2",
    "guard-agent": "2.9.0"
  },
  "docs_bundled_for": {
    "fastapi-guard": "7.8.2",
    "guard-agent": "2.9.0",
    "guard-core": "3.15.0"
  }
}
```

The two sides agree here because this release vendored its docs from those same versions, but they are independent and often will not. Your project pins its own Guard dependencies, so `installed` follows your lockfile while `docs_bundled_for` stays frozen at whatever was current when this release was built. Seeing `installed` trail by a release or two is an ordinary lag, not a fault.

A `null` entry under `installed`, rather than a version that merely differs from `docs_bundled_for`, is the actual warning sign: it means a library you meant to use is entirely absent from the interpreter running the server, not just older or newer than the bundled docs. If a version-specific answer depends on which side is right, trust `installed`, since that is the code actually running; `docs_bundled_for` only tells you which documentation snapshot the search and doc tools are reading.
