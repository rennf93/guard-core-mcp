from urllib.parse import quote

import pytest

from guard_core_mcp.detection import (
    _CaseInsensitiveHeaders,
    _SyntheticRequest,
    check_payload,
    encode_body,
)


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


async def test_malformed_config_returns_structured_errors_instead_of_raising() -> None:
    result = await check_payload(config={"trusted_proxy_depth": "not-an-int"})

    assert result["error"] == "invalid config"
    assert result["errors"][0]["field"] == "trusted_proxy_depth"
    assert "valid integer" in result["errors"][0]["message"]


async def test_header_case_mismatch_no_longer_hides_a_form_encoded_sql_injection() -> (
    None
):
    encoded_payload = quote("1' OR '1'='1")

    result = await check_payload(
        path="/submit",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=f"q={encoded_payload}",
        config={"excluded_detection_body_fields": ["unused"]},
    )

    assert result["is_threat"] is True
    assert result["threat_categories"] == ["sqli"]


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


def test_case_insensitive_headers_look_up_by_any_casing() -> None:
    headers = _CaseInsensitiveHeaders({"Content-Type": "application/json"})

    assert headers["content-type"] == "application/json"
    assert headers.get("CONTENT-TYPE") == "application/json"
    assert list(headers) == ["Content-Type"]
    assert len(headers) == 1


async def test_json_object_body_is_serialized_rather_than_rejected() -> None:
    result = await check_payload(
        path="/api",
        method="POST",
        headers={"Content-Type": "application/json"},
        body={"cmd": "; cat /etc/passwd"},
    )

    assert result["is_threat"] is True


async def test_json_array_body_is_serialized() -> None:
    result = await check_payload(
        path="/api", method="POST", body=["harmless", "values"]
    )

    assert result["is_threat"] is False


def test_encode_body_handles_every_accepted_shape() -> None:
    assert encode_body(None) == b""
    assert encode_body("raw") == b"raw"
    assert encode_body({"a": 1}) == b'{"a": 1}'
    assert encode_body([1, 2]) == b"[1, 2]"
