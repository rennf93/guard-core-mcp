import importlib.metadata
from typing import Any

from mcp.server.fastmcp import FastMCP

from guard_core_mcp import __version__

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


def main() -> None:
    mcp.run()
