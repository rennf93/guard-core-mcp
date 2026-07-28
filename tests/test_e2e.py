import json
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

LAUNCH_SERVER = StdioServerParameters(
    command=sys.executable,
    args=["-c", "from guard_core_mcp.server import main; main()"],
)


@asynccontextmanager
async def running_server() -> AsyncIterator[ClientSession]:
    async with stdio_client(LAUNCH_SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def call(session: ClientSession, tool: str, **arguments: Any) -> Any:
    result = await session.call_tool(tool, arguments)
    return json.loads(result.content[0].text)


@pytest.mark.e2e
async def test_server_starts_and_advertises_every_tool() -> None:
    async with running_server() as session:
        listing = await session.list_tools()

    assert {tool.name for tool in listing.tools} == {
        "versions",
        "validate_config",
        "config_fields",
        "search_docs",
        "get_doc",
        "check_payload",
    }


@pytest.mark.e2e
async def test_versions_reports_this_package_over_the_protocol() -> None:
    from guard_core_mcp import __version__

    async with running_server() as session:
        report = await call(session, "versions")

    assert report["guard_core_mcp"] == __version__
    assert report["installed"]["guard-core"] is not None


@pytest.mark.e2e
async def test_validate_config_flags_an_unknown_field_with_a_suggestion() -> None:
    async with running_server() as session:
        report = await call(
            session,
            "validate_config",
            config={"redis_failopen": True},
            package="fastapi-guard",
        )

    assert report["unknown_fields"][0]["name"] == "redis_failopen"
    assert "redis_fail_open" in report["unknown_fields"][0]["did_you_mean"]


@pytest.mark.e2e
async def test_validate_config_accepts_a_json_body_shaped_config() -> None:
    async with running_server() as session:
        report = await call(
            session,
            "validate_config",
            config={"rate_limit": "not-a-number"},
            package="fastapi-guard",
        )

    assert report["valid"] is False
    assert report["errors"][0]["field"] == "rate_limit"


@pytest.mark.e2e
async def test_config_fields_resolves_an_exact_field() -> None:
    async with running_server() as session:
        report = await call(
            session, "config_fields", query="rate_limit", package="fastapi-guard"
        )

    assert report["exact"]["name"] == "rate_limit"


@pytest.mark.e2e
async def test_search_docs_and_get_doc_round_trip() -> None:
    async with running_server() as session:
        found = await call(session, "search_docs", query="rate limiting", limit=3)
        top = found["results"][0]
        page = await call(session, "get_doc", package=top["package"], path=top["path"])

    assert found["results"]
    assert page["content"]


@pytest.mark.e2e
async def test_check_payload_separates_an_attack_from_a_benign_request() -> None:
    async with running_server() as session:
        attack = await call(
            session, "check_payload", path="/probe", query={"q": "1' OR '1'='1"}
        )
        benign = await call(
            session, "check_payload", path="/probe", query={"page": "2"}
        )

    assert attack["is_threat"] is True
    assert benign["is_threat"] is False


@pytest.mark.e2e
async def test_check_payload_accepts_a_json_object_body() -> None:
    async with running_server() as session:
        report = await call(
            session,
            "check_payload",
            path="/submit",
            method="POST",
            body={"comment": "<script>alert(1)</script>"},
        )

    assert report["is_threat"] is True
