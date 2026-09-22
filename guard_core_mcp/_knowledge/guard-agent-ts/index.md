# guard-agent-ts

The TypeScript telemetry agent for the Guard ecosystem. npm package `guardagent` (not scoped), version 0.1.0, Node >= 20, dual ESM/CJS via tsup, optional peer `ioredis ^5.0.0` for crash-recovery persistence.

## Install

```sh
pnpm add guardagent
pnpm add ioredis   # optional: crash-recovery persistence
```

No git tag exists on the repo yet; `publishConfig.access` is public and npm publication runs through the release workflow on GitHub Release tags, so `pnpm add` only resolves once a publish has actually run.

## Setup

```ts
import { GuardAgent, AgentConfig } from "guardagent";

const agent = new GuardAgent(AgentConfig.create({
  endpoint: "https://api.guard-core.com",
  apiKey: process.env.GUARD_API_KEY!,
  projectId: "my-project",
}));
await agent.start();

agent.sendEvent({ kind: "security_event", payload: { /* ... */ } });

await agent.stop(); // final flush + confirm
```

Config field names are camelCase, 1:1 with the Python agent: `bufferSize` 100, `flushInterval` 30s, `statusInterval` 300s (floor 60s), `highWatermarkRatio` 0.8, `maxConcurrentFlushes` 1, `bufferOverflowPolicy` `drop | block | raise`, `retryAttempts` 3, `timeout` 30s, `backoffFactor` 1.0, `compressionEnabled` true with `compressionThreshold` 1024 bytes, `sensitiveHeaders` redaction defaults (`authorization`, `proxy-authorization`, `cookie`, `x-api-key`), `maxPayloadSize` 1024, optional `redis` config (prefix `guard:agent`), plus `onError` and `logger` hooks. `installId` is auto-generated and sent as `X-Agent-Install-Id`.

## Delivery semantics

At-least-once delivery, 413 split-or-drop, Retry-After backoff (300s cap), permanent-rejection handling on 400/404/422, degraded-state detection, and optional Redis crash recovery; `stop()` does the final flush and confirm.

## Wire contract

`POST /api/v1/events`, `/api/v1/metrics`, `/api/v1/status` with `X-API-Key`, `X-Project-Id`, `X-Agent-Install-Id` and optional `X-Payload-Signature: v1=<hex>` (HMAC-SHA256). The transport signs the **uncompressed** raw JSON bytes before optionally gzipping the wire body, matching the server, which decompresses before verifying.

## Footguns

- The adapters (@guardcore/express, fastify, hono, nestjs) do not wire the agent up for you; @guardcore/core exposes `sendAgentEvent` and an `agentHandler` hook on `initializeSecurityMiddleware` for forwarding.
- Older revisions signed the compressed wire bytes; the fix (branch `fix/uncompressed-signature`) signs the uncompressed body. Verify which revision you actually resolve before debugging signature failures.
