import importlib
import importlib.metadata
import json
from pathlib import Path

import guard_core_mcp.config
import guard_core_mcp.detection
from guard_core_mcp import __version__
from guard_core_mcp.server import (
    GUARD_DISTRIBUTIONS,
    check_payload,
    config_fields,
    get_doc,
    installed_guard_versions,
    main,
    mcp,
    missing_library_error,
    search_docs,
    validate_config,
    versions,
)


def test_versions_reports_every_guard_distribution() -> None:
    report = versions()

    assert report["guard_core_mcp"] == __version__
    assert set(report["installed"]) == set(GUARD_DISTRIBUTIONS)


def test_versions_reports_the_bundled_docs_versions() -> None:
    report = versions()

    manifest_path = (
        Path(__file__).resolve().parent.parent
        / "guard_core_mcp"
        / "_docs"
        / "manifest.json"
    )
    bundled_manifest: dict[str, dict[str, str]] = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    assert report["docs_bundled_for"] == {
        package: bundled_manifest[package]["version"] for package in GUARD_DISTRIBUTIONS
    }


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


def test_missing_library_error_names_the_module() -> None:
    error = missing_library_error(ModuleNotFoundError(name="guard_core"))

    assert "guard_core" in error["error"]
    assert error["hint"]


def test_validate_config_tool_returns_the_report() -> None:
    assert validate_config({"passive_mode": True})["valid"] is True


def test_config_tools_report_a_missing_library_instead_of_raising(monkeypatch) -> None:
    def raise_missing(name: str) -> None:
        raise ModuleNotFoundError(name=name)

    monkeypatch.setattr(importlib, "import_module", raise_missing)
    monkeypatch.setattr(guard_core_mcp.config.importlib, "import_module", raise_missing)

    assert "not installed" in validate_config({})["error"]
    assert "not installed" in config_fields("passive_mode")["error"]


def test_config_tools_report_an_unknown_package() -> None:
    assert "unknown package" in validate_config({}, package="django-guard")["error"]
    assert "unknown package" in config_fields("x", package="django-guard")["error"]


async def test_config_tools_are_registered() -> None:
    registered = {tool.name for tool in await mcp.list_tools()}

    assert {"validate_config", "config_fields"} <= registered


async def test_docs_tools_are_registered() -> None:
    registered = {tool.name for tool in await mcp.list_tools()}

    assert {"search_docs", "get_doc"} <= registered


def test_search_docs_tool_returns_results() -> None:
    assert search_docs("rate limiting")["results"]


def test_get_doc_tool_returns_the_page_content() -> None:
    assert get_doc("guard-core", "index.md")["content"]


async def test_detection_tool_is_registered() -> None:
    registered = {tool.name for tool in await mcp.list_tools()}

    assert {"check_payload"} <= registered


async def test_check_payload_tool_returns_the_detection_report() -> None:
    result = await check_payload(path="/items", query={"q": "1' OR '1'='1"})

    assert result["is_threat"] is True


async def test_check_payload_tool_reports_a_missing_library_instead_of_raising(
    monkeypatch,
) -> None:
    async def raise_missing(*args: object, **kwargs: object) -> None:
        raise ModuleNotFoundError(name="guard_core")

    monkeypatch.setattr(guard_core_mcp.detection, "check_payload", raise_missing)

    result = await check_payload(path="/")

    assert "not installed" in result["error"]
