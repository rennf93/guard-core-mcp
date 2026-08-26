import importlib.metadata
from typing import Any

from mcp.server.mcpserver import MCPServer

from guard_core_mcp import __version__
from guard_core_mcp import config as config_module
from guard_core_mcp import detection as detection_module
from guard_core_mcp import docs as docs_module

GUARD_DISTRIBUTIONS = ("guard-core", "fastapi-guard", "guard-agent")

mcp = MCPServer("guard-core")


def installed_guard_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for distribution in GUARD_DISTRIBUTIONS:
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            versions[distribution] = None
    return versions


@mcp.tool()
def versions() -> dict[str, Any]:
    """Report which Guard libraries this server can introspect, and at what version.

    Also reports this server's own guard-core-mcp version. A null installed version
    means that library is absent from the interpreter running this server, so any
    answer about it would be a guess rather than introspection. Compare installed
    against docs_bundled_for before trusting a documentation answer about a
    version-specific feature.
    """
    return {
        "guard_core_mcp": __version__,
        "installed": installed_guard_versions(),
        "docs_bundled_for": {
            package: entry["version"]
            for package, entry in docs_module.manifest().items()
        },
    }


def missing_library_error(exception: ModuleNotFoundError) -> dict[str, str]:
    return {
        "error": (
            f"{exception.name} is not installed in the interpreter running this server"
        ),
        "hint": (
            "Install guard-core-mcp into the environment that has your Guard libraries "
            "(uv add --dev guard-core-mcp) rather than running it in an isolated one."
        ),
    }


@mcp.tool()
def validate_config(
    config: dict[str, Any], package: str = "fastapi-guard"
) -> dict[str, Any]:
    """Validate a Guard config against the installed library's model.

    Reports type errors, deprecated fields, and unknown keys. Unknown keys matter:
    pydantic silently ignores them, so a misspelled setting does nothing at runtime
    and raises no error anywhere else.

    Also surfaces guard-core's own construction-time misconfiguration warnings
    (logged rather than raised) under construction_warnings: an unknown constructor
    keyword, a trusted_proxies /0 network, and enabled_detection_categories empty
    while penetration detection is enabled all land here as plain messages.

    package is one of fastapi-guard, guard-core, guard-agent.
    """
    try:
        return config_module.validate_config(config, package)
    except ModuleNotFoundError as exception:
        return missing_library_error(exception)
    except ValueError as exception:
        return {"error": str(exception)}


@mcp.tool()
def config_fields(query: str, package: str = "fastapi-guard") -> dict[str, Any]:
    """Look up Guard config settings by name or by what they do.

    An exact field name populates the exact result with that field's type, default,
    required-ness and description. Every query, exact or not, also populates matches
    with every other field whose name or description contains every word of the query
    (case-insensitively, word order does not matter), which is the fastest way to
    answer whether a setting for some behaviour exists at all.

    package is one of fastapi-guard, guard-core, guard-agent.
    """
    try:
        return config_module.config_fields(query, package)
    except ModuleNotFoundError as exception:
        return missing_library_error(exception)
    except ValueError as exception:
        return {"error": str(exception)}


@mcp.tool()
def search_docs(
    query: str, package: str | None = None, limit: int = 5
) -> dict[str, Any]:
    """Search the bundled Guard documentation and return citable pages.

    Covers fastapi-guard, guard-core and guard-agent. Omit package to search all
    three. Each result carries the live documentation URL for that page. Unlike
    validate_config and config_fields, an unrecognized package is not an error here,
    it silently matches nothing, so an empty results list can mean either a real gap
    in the docs or a mistyped package name; if empty, try again with package omitted.
    """
    return docs_module.search_docs(query, package, limit)


@mcp.tool()
def get_doc(package: str, path: str) -> dict[str, Any]:
    """Return the full text of one bundled documentation page.

    Use the package and path from a search_docs result.
    """
    return docs_module.get_doc(package, path)


@mcp.tool()
async def check_payload(
    path: str = "/",
    method: str = "GET",
    query: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    body: str | dict[str, Any] | list[Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a request through guard-core's real detection engine.

    Reports whether the penetration-detection stage flags this request and which
    pattern matched, which is the reliable way to explain a false positive or confirm
    that an attack payload is actually caught. config accepts SecurityConfig fields to
    test how a setting changes the verdict, except enable_redis, which this tool always
    forces to False so the sandbox never touches Redis.

    This is the detection stage alone, not the whole middleware pipeline. A real request
    also passes IP rules, rate limiting, user-agent and cloud-provider checks, any of
    which can block it before detection runs, and a whitelisted IP skips detection
    entirely. So a clean verdict here does not promise the request reaches the route,
    and a threat verdict does not promise the running app would have blocked it.

    body takes either a raw string or a JSON object or array, which is serialized for
    you, so pass the request body in whatever shape you already have it.

    guard-core 3.14.0 scans at most detection_max_scan_values request values (default
    512, names and values counted) per request across the whole detection pass. A
    payload beyond that cap only gets a verdict on the scanned prefix; anything past
    the cap is not inspected.
    """
    try:
        return await detection_module.check_payload(
            path, method, query, headers, body, config
        )
    except ModuleNotFoundError as exception:
        return missing_library_error(exception)


def main() -> None:
    mcp.run()
