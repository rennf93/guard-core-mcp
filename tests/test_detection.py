import pytest

from guard_core_mcp.detection import _SyntheticRequest, check_payload


async def test_sql_injection_in_a_query_parameter_is_a_threat() -> None:
    result = await check_payload(path="/items", query={"q": "1' OR '1'='1"})

    assert result["is_threat"] is True
    assert result["threat_categories"] == ["sqli"]
    assert "matched pattern" in result["trigger_info"]
    assert result["elapsed_ms"] >= 0


async def test_script_tag_is_a_threat() -> None:
    result = await check_payload(
        path="/search", query={"q": "<script>alert(1)</script>"}
    )

    assert result["is_threat"] is True
    assert result["threat_categories"] == ["xss"]


async def test_ordinary_request_is_not_a_threat() -> None:
    result = await check_payload(path="/api/users", query={"page": "2"})

    assert result["is_threat"] is False
    assert result["threat_categories"] == []


async def test_json_body_is_scanned() -> None:
    result = await check_payload(
        path="/api/x",
        method="POST",
        headers={"content-type": "application/json"},
        body='{"name": "; cat /etc/passwd"}',
    )

    assert result["is_threat"] is True


async def test_redis_cannot_be_enabled_by_a_caller_override() -> None:
    result = await check_payload(path="/", config={"enable_redis": True})

    assert result["is_threat"] is False


async def test_redis_override_is_forced_off_in_the_constructed_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import guard_core

    captured: dict[str, object] = {}
    real_security_config = guard_core.SecurityConfig

    class _CapturingSecurityConfig(real_security_config):
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)
            super().__init__(**kwargs)

    monkeypatch.setattr(guard_core, "SecurityConfig", _CapturingSecurityConfig)

    await check_payload(path="/", config={"enable_redis": True})

    assert captured["enable_redis"] is False


async def test_check_payload_writes_nothing_to_stdout(capsys) -> None:
    await check_payload(path="/items", query={"q": "1' OR '1'='1"})

    assert capsys.readouterr().out == ""


def test_synthetic_request_exposes_every_protocol_member() -> None:
    request = _SyntheticRequest(
        path="/x",
        method="POST",
        headers={"a": "b"},
        query_params={"c": "d"},
        body_content=b"z",
    )

    assert request.url_scheme == "https"
    assert request.url_full == "https://sandbox/x"
    assert request.url_replace_scheme("http") == "http://sandbox/x"
    assert request.method == "POST"
    assert request.state is None
    assert request.scope == {}
