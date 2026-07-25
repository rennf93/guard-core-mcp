import importlib.metadata
import typing

import pytest

from guard_core_mcp.config import (
    _format_annotation,
    config_fields,
    describe_field,
    resolve_model,
    validate_config,
)


def test_fastapi_guard_and_guard_core_resolve_to_the_same_model() -> None:
    fastapi_model, fastapi_version = resolve_model("fastapi-guard")
    core_model, core_version = resolve_model("guard-core")

    assert fastapi_model is core_model
    assert fastapi_version != core_version


def test_guard_agent_resolves_to_agent_config() -> None:
    model, _ = resolve_model("guard-agent")

    assert model.__name__ == "AgentConfig"


def test_unknown_package_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown package"):
        resolve_model("django-guard")


def test_valid_config_reports_valid() -> None:
    report = validate_config({"passive_mode": True})

    assert report["valid"] is True
    assert report["errors"] == []
    assert report["unknown_fields"] == []
    assert report["model"] == "SecurityConfig"


def test_type_error_is_reported_as_a_field_error() -> None:
    report = validate_config({"trusted_proxy_depth": "two"})

    assert report["valid"] is False
    assert report["errors"][0]["field"] == "trusted_proxy_depth"
    assert "valid integer" in report["errors"][0]["message"]


def test_typo_is_reported_even_though_pydantic_ignores_it() -> None:
    report = validate_config({"redis_failopen": True})

    assert report["valid"] is False
    assert report["errors"] == []
    assert report["unknown_fields"] == [
        {"name": "redis_failopen", "did_you_mean": ["redis_fail_open"]}
    ]


def test_deprecated_field_is_reported_with_its_name() -> None:
    report = validate_config({"ipinfo_token": "abc"})

    assert report["deprecated"][0]["field"] == "ipinfo_token"
    assert "deprecated" in report["deprecated"][0]["message"]


def test_agent_config_is_validated_against_its_own_model() -> None:
    report = validate_config({"api_key": "k", "endpoint": 7}, package="guard-agent")

    assert report["model"] == "AgentConfig"
    assert report["errors"]


def test_describe_field_reports_metadata_from_the_installed_model() -> None:
    model, _ = resolve_model("guard-core")

    described = describe_field("passive_mode", model.model_fields["passive_mode"])

    assert described["name"] == "passive_mode"
    assert described["type"] == "bool"
    assert described["default"] == "False"
    assert described["required"] is False
    assert "Log-Only" in described["description"]


def test_describe_field_formats_generic_types_and_undefined_defaults() -> None:
    model, _ = resolve_model("guard-core")

    described = describe_field("trusted_proxies", model.model_fields["trusted_proxies"])

    assert described["type"] == "list[str]"
    assert described["default"] is None


def test_format_annotation_falls_back_to_str_for_unnamed_annotations() -> None:
    assert _format_annotation(...) == "Ellipsis"


def test_format_annotation_reports_bare_generic_origin_without_args() -> None:
    assert _format_annotation(typing.Callable) == "Callable"


def test_resolve_model_reports_none_version_when_package_metadata_is_missing(
    monkeypatch,
) -> None:
    def raise_not_found(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", raise_not_found)

    _, version = resolve_model("guard-core")

    assert version is None


def test_exact_name_returns_the_field() -> None:
    result = config_fields("passive_mode")

    assert result["exact"]["name"] == "passive_mode"
    assert result["exact"]["default"] == "False"


def test_multi_word_query_matches_across_name_and_description() -> None:
    names = {match["name"] for match in config_fields("redis timeout")["matches"]}

    assert "redis_socket_connect_timeout" in names


def test_query_matching_only_a_description_still_finds_the_field() -> None:
    names = {match["name"] for match in config_fields("Log-Only")["matches"]}

    assert "passive_mode" in names


def test_misspelled_name_falls_back_to_fuzzy_matches() -> None:
    result = config_fields("redis_failopen")

    assert result["exact"] is None
    assert "redis_fail_open" in {match["name"] for match in result["matches"]}


def test_query_matching_nothing_returns_no_matches() -> None:
    result = config_fields("quantum entanglement")

    assert result["exact"] is None
    assert result["matches"] == []
