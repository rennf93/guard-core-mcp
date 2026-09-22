# guard-agent-php

The PHP telemetry agent for the Guard ecosystem. Composer name `rennf93/guard-agent-php`, requires PHP `^8.2`, `ext-json` and `ext-curl`, and has zero composer dependencies (optional: `ext-redis` and `predis/predis`). Namespace root `RenzoFranceschini\GuardAgent\`.

## Install

```sh
composer require rennf93/guard-agent-php
```

No git tags yet and composer.json carries no `version` field: the version lives in `RenzoFranceschini\GuardAgent\Version::VERSION` (0.1.0) with `USER_AGENT = 'guard-agent/0.1.0'`.

## Setup

```php
$agent = new GuardAgent(AgentConfigResolver::resolve([
    'apiKey' => $_ENV['GUARD_API_KEY'],
    'endpoint' => 'https://api.guard-core.com',
    'projectId' => 'my-project',
    'payloadSigningSecret' => $_ENV['GUARD_SIGNING_SECRET'] ?? null,
]));

$agent->start();
```

Public API: `start()`, `stop()`, `tick()`, `flushBuffer()`, `sendEvent(array)`, `sendMetric(array)`. Defaults from `AgentConfig`: `bufferSize` 100, `flushInterval` 30s, `statusInterval` 300s (floor 60s), `highWatermarkRatio` 0.8, `maxConcurrentFlushes` 1, `bufferOverflowPolicy` Drop (send never throws or blocks), `maxPayloadSize` 1024, `timeout` 30s, `retryAttempts` 3, `backoffFactor` 1.0, `compressionEnabled` true with `compressionThreshold` 1024 bytes.

Request-shutdown shipping: call `flushBuffer()` and `stop()` from `register_shutdown_function` in plain PHP, `kernel.terminate` in Symfony, or the `terminate` hook in Laravel. Long-running workers instead loop `tick()` (cheap: no network I/O unless a trigger fires).

Redis persistence is optional and dependency-free paths exist: `ExtRedisClient`, `PredisRedisClient`, or the built-in `StreamRedisClient` (speaks RESP over streams, no extension needed). Keys look like `{prefix}:agent_events:event_<nanos>_<8hex>` with a 3600s TTL.

## Delivery semantics

Default drop overflow, Retry-After handling, permanent-rejection classification, and a circuit breaker live in `Transport\` (`HttpTransport`, `CircuitBreaker`, `RateLimiter`); the exception taxonomy (`BufferFullException`, `PermanentClientException`, `RateLimitedException`, `PayloadTooLargeException`, ...) is under `Exception\`.

## Wire contract

`POST {endpoint}/api/v1/events`, `/api/v1/metrics`, `/api/v1/status` with `User-Agent: guard-agent/0.1.0`, `X-API-Key`, `X-Agent-Install-Id`, optional `X-Project-Id`, and optional `X-Payload-Signature: v1=<hex>`, where the HMAC-SHA256 covers the **uncompressed** JSON body (the server decompresses gzip before verifying). The 413 cap is 262144 bytes decompressed.

## Footguns

- No tags: composer resolves it from source until a release lands and Packagist submission happens.
- `sendEvent` never throws under the default drop policy; a silent drop is the failure mode, so monitor `AgentStatus`/stats if delivery matters.
- `ext-curl` is required (not suggested): the transport is implemented over curl with gzip bodies.
