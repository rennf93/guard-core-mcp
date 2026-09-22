# guard-agent-rs

The Rust telemetry agent for the Guard ecosystem. Crate `guard-agent-rs` 0.1.0, edition 2024, MSRV 1.92. Standalone: it does not depend on guard-core-engine (stack: reqwest with rustls, tokio, hmac, sha2, flate2, optional redis behind the `persistence` feature).

## Install

```sh
cargo add guard-agent-rs
# with the built-in Redis backend:
cargo add guard-agent-rs --features persistence
```

No git tag exists on the repo yet and nothing is confirmed on crates.io, so verify that `cargo add` resolves before relying on it; otherwise depend on the repo directly.

## Setup

```rust
let mut config = AgentConfig::new("your-api-key-at-least-10-chars");
config.endpoint = "https://api.guard-core.com".to_owned();
config.project_id = Some("proj_your-project".to_owned());
config.payload_signing_secret = Some("server-provided-signing-secret".to_owned());

let agent = GuardAgent::new(config).expect("valid configuration");
agent.start().await;
```

`AgentConfig` fields: `api_key` (minimum 10 characters, sent as `X-API-Key`), `endpoint` (default `https://api.guard-core.com`), `project_id` (sent as `X-Project-Id`), `buffer_size` 100 per kind, `flush_interval` 30s, `status_interval` 300s, `high_watermark_ratio` 0.8, `max_concurrent_flushes` 1, `buffer_overflow_policy` `drop`/`block`/`raise`, `retry_attempts` 3, `timeout` 30s, `backoff_factor` 1.0, `sensitive_headers` redaction list, `max_payload_size`, `compression_enabled` with `compression_threshold` 1024 bytes, `install_id` (persisted at `~/.guard-agent/install-id`), `payload_signing_secret`, and `redis` under the `persistence` feature.

Events: `agent.send_event(SecurityEvent::new("rate_limited").with_ip_address("10.0.0.1").with_endpoint("/api/users").with_action_taken("blocked")).await;` then `agent.stop().await` at shutdown for the final flush. `flush_buffer()`, `get_status()` and `get_stats()` are available for manual control.

## Delivery semantics

Buffer, watermark and overflow defaults mirror the other agents; 429 honors `Retry-After`; 413 splits or drops; 400/404/422 are permanent; gzip applies above the compression threshold.

## Wire contract

`POST {endpoint}/api/v1/events`, `/api/v1/metrics`, `/api/v1/status`. The HMAC signature covers the **uncompressed** JSON body (`X-Payload-Signature: v1=<hex>`), which is what the server verifies after its gzip middleware decompresses the request.

## Footguns

- No tag and no confirmed crates.io release at the time of writing; treat the install line as aspirational until one exists.
- Redis persistence is feature-gated (`--features persistence`); without it there is no crash recovery.
