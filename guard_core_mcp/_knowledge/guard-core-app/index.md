# guard-core-app (SaaS ingestion contract)

The SaaS platform (api.guard-core.com) that receives telemetry from every Guard agent. The contract below is verified against `backend/guard-core-api/guard_core_api/api/routers/telemetry_router.py` and its middleware/services. The repo tags by calendar date (latest at time of writing: 2026.09.19); AGENTS.md and CLAUDE.md exist, there is no SKILL.md.

## Endpoints

All mounted under the `/api/v1` prefix:

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/events` | batch security events |
| `POST /api/v1/metrics` | batch metrics; doubles as the heartbeat |
| `POST /api/v1/status` | agent status beacon |
| `GET /api/v1/status` | agent-facing status probe |
| `POST /api/v1/events/encrypted` | AES-256-GCM envelope variant (used by the Python agent when `project_encryption_key` is set) |

## Headers

- `X-API-Key`: required.
- `X-Project-Id`: optional.
- `X-Agent-Install-Id`: optional; honored only when install-id tracking is enabled server-side.
- `X-Payload-Signature`: optional; `v1=` plus lowercase hex HMAC-SHA256.
- `Content-Encoding: gzip` when the body is compressed.

## Compression and signing

`GzipRequestMiddleware` decompresses gzip bodies before route handlers run (stripping `content-encoding` and rewriting `content-length`; malformed gzip gets a 400). Signature verification (`services/payload_signature.py`) strips the `v1=` prefix and compares an HMAC-SHA256 hex digest over the **decompressed** body with `hmac.compare_digest`. Because middleware runs first, `request.body()` inside the router is already uncompressed, so the effective contract is: sign the uncompressed body. Failure returns 401 "Invalid payload signature" only when `INGEST_REQUIRE_SIGNED_PAYLOADS` is enabled, otherwise it logs a warning.

## Limits

`INGEST_MAX_PAYLOAD_BYTES` defaults to 262144 (256 KiB) and is enforced by `enforce_payload_size` against the decompressed length: a missing `Content-Length` gets 411, an unparsable one 400, and anything over the cap 413. Client-side, agents compress above a 1024-byte threshold and cap single event payloads at 1024 bytes.

## Response semantics

- `200`: accepted. The `TelemetryResponse` body carries `success`, `events_dropped_invalid_timestamp` and `errors`; `success: false` or a non-empty `errors` means a partial failure, and agents requeue the batch in memory, retain their Redis keys and back off.
- `429`: rate limited by three token buckets (per-IP, per-API-key, per-project), always with a `Retry-After` header (seconds, minimum 1). Agents must buffer and retry, never drop; the client-side Retry-After cap is 300s.
- `413`: payload too large; agents split the batch in half recursively or drop the singleton.
- `400/404/422`: classified as permanent rejections agent-side (`_NON_RETRYABLE_STATUS_CODES` also includes 413, reached only after the split attempt); the batch is dropped, never retried.
- `401/403`: invalid API key or project ID, and IP-allowlist denials.
- `503`: transient (database contention or a tripped circuit breaker), carries `Retry-After`.

## Footguns

- guard-agent 3.0.0 (Python) signs after compression (`_maybe_compress` runs before `sign_payload`), so when a body exceeds the compression threshold its signature covers compressed bytes while the server verifies uncompressed bytes; signed and gzipped batches fail verification when `require_signed_payloads` is enabled. The Go, TypeScript, PHP and Rust agents sign the uncompressed body and match the contract.
- 413 is both a "split and retry" signal and part of the permanent-rejection tuple; agents try the recursive split first and only drop a singleton that still exceeds the cap.
- The public agent-facing docs live in the frontend content tree (`frontend/src/content/docs/reference/01-agent-telemetry-api.mdx`), not the repo-root docs/ directory.
