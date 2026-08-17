import json
import time
import types
from collections.abc import Iterator, Mapping
from typing import Any

from pydantic import ValidationError

from guard_core_mcp import config as config_module


class _CaseInsensitiveHeaders(Mapping[str, str]):
    def __init__(self, headers: Mapping[str, str]) -> None:
        self._original = dict(headers)
        self._lowercased = {key.lower(): value for key, value in self._original.items()}

    def __getitem__(self, key: str) -> str:
        return self._lowercased[key.lower()]

    def __iter__(self) -> Iterator[str]:
        return iter(self._original)

    def __len__(self) -> int:
        return len(self._original)


def _headers_with_content_length(
    headers: Mapping[str, str], body_content: bytes
) -> dict[str, str]:
    merged = dict(headers)
    if body_content and not any(key.lower() == "content-length" for key in merged):
        merged["content-length"] = str(len(body_content))
    return merged


class _SyntheticRequest:
    def __init__(
        self,
        path: str,
        method: str,
        headers: Mapping[str, str],
        query_params: Mapping[str, str],
        body_content: bytes,
    ) -> None:
        self._path = path
        self._method = method
        self._headers = _CaseInsensitiveHeaders(
            _headers_with_content_length(headers, body_content)
        )
        self._query_params = query_params
        self._body = body_content
        self._state = types.SimpleNamespace()

    @property
    def url_path(self) -> str:
        return self._path

    @property
    def url_scheme(self) -> str:
        return "https"

    @property
    def url_full(self) -> str:
        return f"https://sandbox{self._path}"

    def url_replace_scheme(self, scheme: str) -> str:
        return f"{scheme}://sandbox{self._path}"

    @property
    def method(self) -> str:
        return self._method

    @property
    def client_host(self) -> str:
        return "127.0.0.1"

    @property
    def headers(self) -> Mapping[str, str]:
        return self._headers

    @property
    def query_params(self) -> Mapping[str, str]:
        return self._query_params

    async def body(self) -> bytes:
        return self._body

    @property
    def state(self) -> Any:
        return self._state

    @property
    def scope(self) -> dict[str, Any]:
        return {}


def encode_body(body: str | dict[str, Any] | list[Any] | None) -> bytes:
    if body is None:
        return b""
    if isinstance(body, str):
        return body.encode()
    return json.dumps(body).encode()


async def check_payload(
    path: str = "/",
    method: str = "GET",
    query: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    body: str | dict[str, Any] | list[Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from guard_core import SecurityConfig
    from guard_core.protocols.request_protocol import GuardRequest
    from guard_core.utils import detect_penetration_attempt

    try:
        security_config = SecurityConfig(**{**(config or {}), "enable_redis": False})
    except ValidationError as exception:
        return {
            "error": "invalid config",
            "errors": config_module.parse_validation_error(exception),
        }
    request: GuardRequest = _SyntheticRequest(
        path=path,
        method=method,
        headers=headers or {},
        query_params=query or {},
        body_content=encode_body(body),
    )

    started = time.perf_counter()
    result = await detect_penetration_attempt(request, security_config)
    elapsed_ms = (time.perf_counter() - started) * 1000

    return {
        "is_threat": result.is_threat,
        "trigger_info": result.trigger_info,
        "threat_categories": list(result.threat_categories),
        "threat_scores": dict(result.threat_scores),
        "elapsed_ms": round(elapsed_ms, 2),
    }
