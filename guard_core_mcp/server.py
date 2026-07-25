import importlib.metadata
from typing import Any

from mcp.server.fastmcp import FastMCP

from guard_core_mcp import __version__
from guard_core_mcp import config as config_module

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


def main() -> None:
    mcp.run()
