# guard-agent-go

The Go telemetry agent for the Guard ecosystem. Module `github.com/rennf93/guard-agent-go`, package `guardagent`, directive `go 1.25.0`. It is standalone: its only dependency is `redis/go-redis/v9`, and it does not depend on guard-core-go.

## Install

```sh
go get github.com/rennf93/guard-agent-go@main
```

No release tag yet; the README says to pin a commit or track main until the first `v*` tag. Version 0.1.0 comes from the `Version` constant in `version.go`.

## Setup

`guardagent.DefaultConfig()` returns a `Config` (a value, not a pointer) that you mutate and pass to `guardagent.New(cfg)`, then `agent.Start(ctx)` / `agent.Stop(ctx)`, `agent.SendEvent(ctx, SecurityEvent{...})`, `agent.SendMetric(ctx, SecurityMetric{...})`, `agent.Status()`. Key defaults: `APIKey` required (minimum 10 characters), `Endpoint` `https://api.guard-core.com`, `BufferSize` 100 per kind, `FlushInterval` 30s, `StatusInterval` 300s (floor 60s), `HighWatermarkRatio` 0.8, `MaxConcurrentFlushes` 1, `Overflow` `drop` (also `block` and `raise` returning `*BufferFullError`), `RetryAttempts` 3, `Timeout` 30s, gzip enabled above 1024 bytes, `InstallID` persisted at `~/.guard-agent/install-id`, optional `Redis` (`URL`, `Prefix` `guard:agent`, `TTL` 1h).

## Delivery semantics

At-least-once handshake (drain, send, confirm-or-requeue in original order). 429 honors `Retry-After` (60s default, 300s cap). 413 splits the batch recursively in half. 400/404/422 are permanent drops. 401/403/5xx/network errors back off exponentially behind a circuit breaker (5 failures in 60s, half-open probe). `Stop` performs one final flush that bypasses backoff gates. Redis persistence fails open: writes pause 30s after 3 consecutive failures.

## Wire contract

`POST {endpoint}/api/v1/events`, `/api/v1/metrics`, `/api/v1/status` with headers `X-API-Key`, `X-Project-Id`, optional `X-Payload-Signature`. Signing is HMAC-SHA256 over the **uncompressed** JSON body, delivered as `v1=` plus the lowercase hex digest; the server verifies after its gzip middleware decompresses.

## Footguns

- No adapter forwards telemetry automatically: call `SendEvent`/`SendMetric` from your handlers or middleware yourself.
- `New` takes a `Config` value plus variadic `Option`, not a pointer.
- Set `SigningSecret` from `INGEST_PAYLOAD_SIGNING_SECRET`; an empty secret means the signature header is simply omitted.
