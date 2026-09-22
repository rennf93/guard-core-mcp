# guard-core-php

The PHP port of the guard-core security engine. Composer name `rennf93/guard-core-php`, requires PHP `^8.2` plus `ext-pcre`, `ext-mbstring` and `ext-json`. Namespace root `RenzoFranceschini\GuardCore\`.

## Install

```sh
composer require rennf93/guard-core-php
```

Tagged `v0.1.0`, but not on Packagist yet: until the Packagist submission lands, point composer at the repository and allow dev stability.

```json
{
    "minimum-stability": "dev",
    "prefer-stable": true,
    "repositories": [
        { "type": "vcs", "url": "https://github.com/rennf93/guard-core-php" }
    ]
}
```

composer.json carries no `version` field (the tag carries it).

## Setup

- `RenzoFranceschini\GuardCore\Config\SecurityConfig` is the config object (named arguments: `enableRedis`, `blacklist`, `rateLimit`, `rateLimitWindow`, `enableRateLimiting`, ...).
- `RenzoFranceschini\GuardCore\Engine\GuardEngine` is the engine; `execute(GuardRequest $request): ?GuardResponse` is the main entry point.
- `Request\SimpleGuardRequest` builds a request without a framework; `Request\GuardResponseFactory` produces responses. Adapters (psr15-guard, laravel-guard, symfony-guard, slim-guard) translate their framework's request/response into these types.

## Conformance

`composer conformance` runs `bin/conformance.php` over the vendored spec 4.0.2 corpus (163 cases).

## Footguns

- No AGENTS.md, CLAUDE.md or SKILL.md exist in this repo (every other port has them), and the README is a three-line stub, so API knowledge lives in the code and the adapter READMEs.
- `KNOWN_GAPS.md` (on disk, gitignored) tracks open gaps found by the adapter test suites, including PCRE JIT stack exhaustion on very large scan subjects under stock php.ini defaults, where the engine fails secure (500) rather than passing a request unchecked.
- The repo name is `guard-core-php` but the vendor name is `rennf93/`, so path repos in adapters use `../guard-core-php` with `"canonical": false`.
