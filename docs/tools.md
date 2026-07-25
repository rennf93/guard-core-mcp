---

title: Tools - Guard Core MCP
description: Signature, parameters, and example call and response for each of the six guard-core-mcp tools
keywords: mcp tools, fastapi-guard, guard-core, guard-agent, validate_config, check_payload
---

Tools
=====

All six tools are registered in `guard_core_mcp/server.py`. `validate_config`, `config_fields`,
`search_docs` and `get_doc` all accept a `package` argument that should be one of `fastapi-guard`,
`guard-core` or `guard-agent`, but they don't validate it the same way. `validate_config` and
`config_fields` reject an unrecognized value with
`{"error": "unknown package '<value>'; expected one of guard-core, fastapi-guard, guard-agent"}`.
`search_docs` has no such check — an unrecognized `package` just matches nothing, so it returns
`{"query": ..., "results": []}`. `get_doc` returns `{"error": "unknown doc path"}` for either an
unrecognized `package` or a `path` that doesn't exist under it — the two cases aren't
distinguished in the response.

`validate_config`, `config_fields` and `check_payload` depend on the corresponding library being
installed in the interpreter running the server. If it is not, they return a structured
`{"error": ..., "hint": ...}` instead of raising — see
[Installation](installation.md#why-not-uvx-guard-core-mcp) for exactly what that looks like and
why.

___

`versions`
----------

```python
def versions() -> dict[str, Any]
```

No parameters. Reports which Guard libraries this server can introspect, at what version, and
which library versions the bundled documentation covers. A `null` installed version means that
library is absent from this interpreter, so any answer about it would be a guess rather than
introspection.

**Example call**:

```python
versions()
```

**Example response**:

```json
{
  "guard_core_mcp": "0.1.0",
  "installed": {
    "guard-core": "3.5.0",
    "fastapi-guard": "7.3.0",
    "guard-agent": "2.7.0"
  },
  "docs_bundled_for": {
    "fastapi-guard": "7.3.0",
    "guard-agent": "2.7.0",
    "guard-core": "3.5.0"
  }
}
```

___

`validate_config`
------------------

```python
def validate_config(config: dict[str, Any], package: str = "fastapi-guard") -> dict[str, Any]
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `config` | `dict[str, Any]` | required | The config dict to validate |
| `package` | `str` | `"fastapi-guard"` | One of `fastapi-guard`, `guard-core`, `guard-agent` |

Validates `config` against the installed library's real Pydantic model (`SecurityConfig` for
`fastapi-guard`/`guard-core`, `AgentConfig` for `guard-agent`) and reports three separate kinds of
problems: unknown keys pydantic would otherwise silently ignore (with typo suggestions),
validation errors, and `DeprecationWarning`s the model raises for fields that still work but
shouldn't be used.

**Example call — a deprecated field**:

```python
validate_config({"ipinfo_token": "abc123"}, "fastapi-guard")
```

**Example response**:

```json
{
  "valid": true,
  "package": "fastapi-guard",
  "version": "7.3.0",
  "model": "SecurityConfig",
  "errors": [],
  "unknown_fields": [],
  "deprecated": [
    {
      "field": "ipinfo_token",
      "message": "ipinfo_token is deprecated and will be removed in a future release; create a custom geo_ip_handler instead."
    }
  ]
}
```

**Example call — a typo'd field**:

```python
validate_config({"rate_limit": 100, "enable_rate_limit": True}, "fastapi-guard")
```

**Example response**:

```json
{
  "valid": false,
  "package": "fastapi-guard",
  "version": "7.3.0",
  "model": "SecurityConfig",
  "errors": [],
  "unknown_fields": [
    {
      "name": "enable_rate_limit",
      "did_you_mean": ["enable_rate_limiting"]
    }
  ],
  "deprecated": []
}
```

`enable_rate_limit` isn't a `SecurityConfig` field — the real one is `enable_rate_limiting` —
and Pydantic would have accepted and then ignored it silently. A type error (for example
`{"rate_limit": "not-a-number"}`) instead produces an entry in `errors`, each with `field`,
`message`, and the offending `input`.

___

`config_fields`
----------------

```python
def config_fields(query: str, package: str = "fastapi-guard") -> dict[str, Any]
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `query` | `str` | required | An exact field name, or free text to match against field names and descriptions |
| `package` | `str` | `"fastapi-guard"` | One of `fastapi-guard`, `guard-core`, `guard-agent` |

An exact field name populates `exact` with that field's type, default, required-ness and
description. Any other query is matched (case-insensitively, every token must appear) against
every field name and description; if nothing matches, `matches` falls back to the closest field
names by fuzzy string distance.

**Example call**:

```python
config_fields("rate_limit", "fastapi-guard")
```

**Example response**:

```json
{
  "package": "fastapi-guard",
  "version": "7.3.0",
  "query": "rate_limit",
  "exact": {
    "name": "rate_limit",
    "type": "int",
    "default": "10",
    "required": false,
    "description": "Maximum requests per rate_limit_window"
  },
  "matches": [
    {
      "name": "rate_limit_window",
      "type": "int",
      "default": "60",
      "required": false,
      "description": "Rate limiting time window (seconds)"
    },
    {
      "name": "enable_rate_limiting",
      "type": "bool",
      "default": "True",
      "required": false,
      "description": "Enable/disable rate limiting functionality"
    },
    {
      "name": "endpoint_rate_limits",
      "type": "dict[str, tuple[int, int]]",
      "default": null,
      "required": false,
      "description": "Per-endpoint rate limits set by dynamic rules"
    }
  ]
}
```

`matches` here still lists every other field whose name or description contains `rate_limit`,
alongside the `exact` hit, which is how this doubles as "does a setting for X exist at all". A
typo'd query with no token match at all — `"rate_limti"`, say — falls through to the fuzzy
fallback instead, which is `matches` populated purely from `difflib.get_close_matches` against
every field name, with `exact` still `null`.

___

`search_docs`
--------------

```python
def search_docs(query: str, package: str | None = None, limit: int = 5) -> dict[str, Any]
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `query` | `str` | required | Free-text search terms |
| `package` | `str \| None` | `None` | One of `fastapi-guard`, `guard-core`, `guard-agent`; omit to search all three |
| `limit` | `int` | `5` | Maximum number of results |

Searches the bundled documentation (`guard_core_mcp/_docs/`) by counting query-term occurrences
per page, and returns the highest-scoring pages with the best-matching heading and a snippet.
Each result carries `url`, the live documentation URL for that page, built from the manifest
recorded when the docs were vendored — this works even when the underlying library isn't
installed, since the docs ship inside the wheel.

**Example call**:

```python
search_docs("rate limiting", "fastapi-guard", limit=3)
```

**Example response**:

```json
{
  "query": "rate limiting",
  "results": [
    {
      "package": "fastapi-guard",
      "path": "tutorial/decorators/rate-limiting.md",
      "heading": "",
      "snippet": "description: Learn how to use rate limiting decorators for custom request rate controls and geographic rate limiting",
      "url": "https://rennf93.github.io/fastapi-guard/latest/tutorial/decorators/rate-limiting/",
      "score": 115
    },
    {
      "package": "fastapi-guard",
      "path": "tutorial/ip-management/rate-limiter.md",
      "heading": "",
      "snippet": "Rate limiting is a crucial security feature that protects your API from abuse, DoS attacks, and excessive usage. FastAPI Guard provides a robust rate limiting system through the dedicated `RateLimitManager` class.",
      "url": "https://rennf93.github.io/fastapi-guard/latest/tutorial/ip-management/rate-limiter/",
      "score": 69
    },
    {
      "package": "fastapi-guard",
      "path": "release-notes.md",
      "heading": "",
      "snippet": "- **Geographic rate limit check**: Fixed geo-based rate limiting by implementing the missing `_check_geo_rate_limit` method in `RateLimitCheck`. Previously, geo rate limits configured via the `@security.geo_rate_limit` decorator were stored but never enforced. The rate limit pipeline now correctly e",
      "url": "https://rennf93.github.io/fastapi-guard/latest/release-notes/",
      "score": 67
    }
  ]
}
```

`path` and `package` from a result feed directly into `get_doc`.

___

`get_doc`
---------

```python
def get_doc(package: str, path: str) -> dict[str, Any]
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `package` | `str` | required | One of `fastapi-guard`, `guard-core`, `guard-agent` |
| `path` | `str` | required | A relative path from a `search_docs` result, e.g. `installation.md` |

Returns the full text of one bundled documentation page. `path` is resolved relative to that
package's vendored docs root and rejected — as `{"error": "unknown doc path"}` — if it would
escape that root or doesn't exist, so this cannot be used to read arbitrary files.

**Example call**:

```python
get_doc("fastapi-guard", "installation.md")
```

**Example response** (content truncated here; the real response returns the full page)

```json
{
  "package": "fastapi-guard",
  "path": "installation.md",
  "url": "https://rennf93.github.io/fastapi-guard/latest/installation/",
  "content": "---\n\ntitle: Installation - FastAPI Guard\ndescription: Learn how to install and set up FastAPI Guard, a comprehensive security middleware for FastAPI applications\nkeywords: fastapi guard installation, python security middleware, fastapi security setup\n---\n\nInstallation\n============\n\nInstall `fastapi-..."
}
```

___

`check_payload`
----------------

```python
async def check_payload(
    path: str = "/",
    method: str = "GET",
    query: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    body: str | dict[str, Any] | list[Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str` | `"/"` | Request path |
| `method` | `str` | `"GET"` | HTTP method |
| `query` | `dict[str, str] \| None` | `None` | Query parameters |
| `headers` | `dict[str, str] \| None` | `None` | Request headers |
| `body` | `str \| dict \| list \| None` | `None` | Request body. A raw string is sent as-is; a JSON object or array is serialized for you |
| `config` | `dict[str, Any] \| None` | `None` | `SecurityConfig` fields to test how a setting changes the verdict |

The only async tool. Builds a synthetic request from the arguments and runs it through
guard-core's real `detect_penetration_attempt`, using a `SecurityConfig` built from `config`
(defaulting to guard-core's defaults) with `enable_redis` always forced to `False` — the sandbox
never touches Redis, so results are Redis-independent by construction. `elapsed_ms` reflects
actual detection time for that call and varies between runs; the values below are one real
sample, not a promise. `headers` is matched case-insensitively, the same way guard-core's own
`GuardRequest` protocol requires. A `config` value that fails `SecurityConfig` validation returns
`{"error": "invalid config", "errors": [...]}`, with each entry in the same `field`/`message`/
`input` shape `validate_config` reports for the identical failure.

**Example call — a SQL injection payload**:

```python
await check_payload(path="/search", method="GET", query={"q": "1' OR '1'='1"})
```

**Example response**:

```json
{
  "is_threat": true,
  "trigger_info": "Query param 'q': Value matched pattern '(?i)(?:OR|AND)\\s+'[\\w\\d]*'='[\\w\\d]*'?'",
  "threat_categories": ["sqli"],
  "threat_scores": {"sqli": 1.0},
  "elapsed_ms": 4.35
}
```

**Example call — a benign request**:

```python
await check_payload(path="/search", method="GET", query={"q": "hello world"})
```

**Example response**:

```json
{
  "is_threat": false,
  "trigger_info": "",
  "threat_categories": [],
  "threat_scores": {},
  "elapsed_ms": 2.67
}
```
