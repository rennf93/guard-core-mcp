import importlib.metadata

from guard_core_mcp import __version__
from guard_core_mcp.server import (
    GUARD_DISTRIBUTIONS,
    installed_guard_versions,
    main,
    mcp,
    versions,
)


def test_versions_reports_every_guard_distribution() -> None:
    report = versions()

    assert report["guard_core_mcp"] == __version__
    assert set(report["installed"]) == set(GUARD_DISTRIBUTIONS)


def test_absent_distribution_reports_none_instead_of_raising(monkeypatch) -> None:
    def raise_not_found(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", raise_not_found)

    assert installed_guard_versions() == dict.fromkeys(GUARD_DISTRIBUTIONS, None)


async def test_versions_is_registered_as_a_tool() -> None:
    assert "versions" in {tool.name for tool in await mcp.list_tools()}


def test_main_starts_the_server(monkeypatch) -> None:
    started = []
    monkeypatch.setattr(mcp, "run", lambda: started.append(True))

    main()

    assert started == [True]
