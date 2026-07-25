import importlib.metadata
from typing import Any

from mcp.server.fastmcp import FastMCP

from guard_core_mcp import __version__
from guard_core_mcp import config as config_module
from guard_core_mcp import detection as detection_module
from guard_core_mcp import docs as docs_module

GUARD_DISTRIBUTIONS = ("guard-core", "fastapi-guard", "guard-agent")

mcp = FastMCP("guard-core")


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

    A null version means that library is not installed in the interpreter running
    this server, so any answer about it would be a guess rather than introspection.
    """
    return {
        "guard_core_mcp": __version__,
        "installed": installed_guard_versions(),
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

    An exact field name returns that field's type, default and description. Anything
    else is matched against every field name and description, which is the fastest way
    to answer whether a setting for some behaviour exists at all.

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
    three. Each result carries the live documentation URL for that page.
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
    body: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a request through guard-core's real detection engine.

    Answers whether a given request would be blocked and which pattern matched,
    which is the reliable way to explain a false positive or confirm that an attack
    payload is actually caught. config accepts SecurityConfig fields to test how a
    setting changes the verdict.
    """
    try:
        return await detection_module.check_payload(
            path, method, query, headers, body, config
        )
    except ModuleNotFoundError as exception:
        return missing_library_error(exception)


def main() -> None:
    mcp.run()
