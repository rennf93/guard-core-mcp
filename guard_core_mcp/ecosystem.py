from typing import Any

from pydantic import BaseModel


class EngineInfo(BaseModel):
    package: str
    repo: str
    version: str
    install: str
    release_status: str
    conformance: str
    notes: str = ""


class AdapterInfo(BaseModel):
    package: str
    repo: str
    version: str
    install: str
    release_status: str
    framework: str
    role: str
    python_counterpart: str
    counterpart_rationale: str
    snippet_language: str
    snippet: str
    notes: str = ""


class AgentInfo(BaseModel):
    package: str
    repo: str
    version: str
    install: str
    release_status: str
    semantics: str
    integration: str
    snippet_language: str
    snippet: str
    notes: str = ""


class LanguageEntry(BaseModel):
    language: str
    label: str
    engine: EngineInfo
    adapters: list[AdapterInfo]
    agent: AgentInfo


class ConformanceInfo(BaseModel):
    reference: str
    spec_version: str
    cases: int
    suites: int
    engine_commit: str
    corpus: str
    interop: str


class SaaSContract(BaseModel):
    base_url: str
    endpoints: dict[str, str]
    headers: dict[str, str]
    signing: str
    compression: str
    limits: dict[str, str]
    response_semantics: dict[str, str]
    known_quirks: list[str]


class EcosystemRegistry(BaseModel):
    languages: dict[str, LanguageEntry]
    conformance: ConformanceInfo
    saas: SaaSContract


GO_ENGINE = EngineInfo(
    package="guard-core-go",
    repo="https://github.com/rennf93/guard-core-go",
    version="0.1.0",
    install="go get github.com/rennf93/guard-core-go@v0.1.0",
    release_status="tagged",
    conformance=(
        "spec-4.0.3 corpus vendored at conformance/guard-core-spec-4.0.3 "
        "(184 cases across 12 suites), fail-closed baseline"
    ),
    notes=(
        "module github.com/rennf93/guard-core-go, go 1.25.0; the only tag is the "
        "v0.1.0 pre-release snapshot; the README is a stub, so usage lives in the "
        "adapter READMEs and AGENTS.md"
    ),
)

GO_NETHTTP_SNIPPET = r"""package main

import (
	"log"
	"net/http"

	guardcore "github.com/rennf93/guard-core-go/guardcore"
	nethttp "github.com/rennf93/nethttp-guard"
)

func main() {
	cfg := guardcore.DefaultSecurityConfig()
	engine, err := guardcore.NewEngine(cfg)
	if err != nil {
		log.Fatal(err)
	}
	if err := engine.Initialize(); err != nil {
		log.Fatal(err)
	}

	guard, err := nethttp.New(engine)
	if err != nil {
		log.Fatal(err)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		_, _ = w.Write([]byte("ok"))
	})

	log.Fatal(http.ListenAndServe(":8080", guard(mux)))
}"""

GO_GIN_SNIPPET = r"""package main

import (
	"log"

	ginlib "github.com/gin-gonic/gin"
	guardcore "github.com/rennf93/guard-core-go/guardcore"
	guardgin "github.com/rennf93/gin-guard"
)

func main() {
	cfg := guardcore.DefaultSecurityConfig()
	engine, err := guardcore.NewEngine(cfg)
	if err != nil {
		log.Fatal(err)
	}
	if err := engine.Initialize(); err != nil {
		log.Fatal(err)
	}

	guard, err := guardgin.New(engine)
	if err != nil {
		log.Fatal(err)
	}

	router := ginlib.New()
	router.Use(guard)
	router.GET("/", func(c *ginlib.Context) {
		c.String(200, "ok")
	})

	log.Fatal(router.Run(":8080"))
}"""

GO_ECHO_SNIPPET = r"""package main

import (
	"log"

	echolib "github.com/labstack/echo/v4"
	guardcore "github.com/rennf93/guard-core-go/guardcore"
	guardecho "github.com/rennf93/echo-guard"
)

func main() {
	cfg := guardcore.DefaultSecurityConfig()
	engine, err := guardcore.NewEngine(cfg)
	if err != nil {
		log.Fatal(err)
	}
	if err := engine.Initialize(); err != nil {
		log.Fatal(err)
	}

	guard, err := guardecho.New(engine)
	if err != nil {
		log.Fatal(err)
	}

	router := echolib.New()
	router.Use(guard)
	router.GET("/", func(c echolib.Context) error {
		return c.String(200, "ok")
	})

	log.Fatal(router.Start(":8080"))
}"""

GO_FIBER_SNIPPET = r"""package main

import (
	"log"

	fiberlib "github.com/gofiber/fiber/v3"
	guardcore "github.com/rennf93/guard-core-go/guardcore"
	guardfiber "github.com/rennf93/fiber-guard"
)

func main() {
	cfg := guardcore.DefaultSecurityConfig()
	engine, err := guardcore.NewEngine(cfg)
	if err != nil {
		log.Fatal(err)
	}
	if err := engine.Initialize(); err != nil {
		log.Fatal(err)
	}

	guard, err := guardfiber.New(engine)
	if err != nil {
		log.Fatal(err)
	}

	app := fiberlib.New()
	app.Use(guard)
	app.Get("/", func(c fiberlib.Ctx) error {
		return c.SendString("ok")
	})

	log.Fatal(app.Listen(":8080"))
}"""

GO_AGENT_SNIPPET = r"""cfg := guardagent.DefaultConfig()
cfg.APIKey = "your-ingest-api-key"
cfg.ProjectID = "your-project-id"
// cfg.Endpoint = "https://your-guard-core-app.example.com"

agent, err := guardagent.New(cfg)
if err != nil {
	log.Fatal(err)
}
if err := agent.Start(context.Background()); err != nil {
	log.Fatal(err)
}
defer func() { _ = agent.Stop(context.Background()) }()

ctx := context.Background()
if err := agent.SendEvent(ctx, guardagent.SecurityEvent{
	EventType: "penetration_attempt",
	IPAddress: "203.0.113.7",
	Method:    "GET",
	Endpoint:  "/admin",
	Reason:    "suspicious pattern",
}); err != nil {
	log.Printf("telemetry: %v", err)
}
_ = agent.SendMetric(ctx, guardagent.SecurityMetric{
	MetricType: guardagent.MetricRequestCount,
	Value:      1,
})"""

GO_ENTRY = LanguageEntry(
    language="go",
    label="Go",
    engine=GO_ENGINE,
    adapters=[
        AdapterInfo(
            package="nethttp-guard",
            repo="https://github.com/rennf93/nethttp-guard",
            version="0.1.0",
            install=(
                "go get github.com/rennf93/nethttp-guard "
                "github.com/rennf93/guard-core-go@v0.1.0"
            ),
            release_status="tagged",
            framework="nethttp",
            role="net/http middleware (func(http.Handler) http.Handler)",
            python_counterpart="flaskapi-guard",
            counterpart_rationale=(
                "sync handler-chain middleware over the standard library, matching "
                "the sync-mirror integration style"
            ),
            snippet_language="go",
            snippet=GO_NETHTTP_SNIPPET,
            notes=(
                "options: WithMaxBodyBytes (default 262144), WithLogger, "
                "WithRouteID; route config via engine.Routes.Register; engine "
                "malfunctions fail closed with a 500"
            ),
        ),
        AdapterInfo(
            package="gin-guard",
            repo="https://github.com/rennf93/gin-guard",
            version="unreleased",
            install=(
                "go get github.com/rennf93/gin-guard@main "
                "github.com/rennf93/guard-core-go@v0.1.0"
            ),
            release_status="untagged",
            framework="gin",
            role="Gin middleware (gin.HandlerFunc via router.Use)",
            python_counterpart="flaskapi-guard",
            counterpart_rationale=("sync middleware chain around synchronous handlers"),
            snippet_language="go",
            snippet=GO_GIN_SNIPPET,
            notes=(
                "no release tag yet; pin a commit or track main; import with the "
                "alias guardgin because the package name collides with gin-gonic"
            ),
        ),
        AdapterInfo(
            package="echo-guard",
            repo="https://github.com/rennf93/echo-guard",
            version="unreleased",
            install=(
                "go get github.com/rennf93/echo-guard@main "
                "github.com/rennf93/guard-core-go@v0.1.0"
            ),
            release_status="untagged",
            framework="echo",
            role="Echo middleware (echo.MiddlewareFunc via router.Use)",
            python_counterpart="flaskapi-guard",
            counterpart_rationale=("sync middleware chain around synchronous handlers"),
            snippet_language="go",
            snippet=GO_ECHO_SNIPPET,
            notes=(
                "no release tag yet; pin a commit or track main; import with the "
                "alias guardecho because the package name collides with labstack"
            ),
        ),
        AdapterInfo(
            package="fiber-guard",
            repo="https://github.com/rennf93/fiber-guard",
            version="unreleased",
            install=(
                "go get github.com/rennf93/fiber-guard@main "
                "github.com/rennf93/guard-core-go@v0.1.0"
            ),
            release_status="untagged",
            framework="fiber",
            role="Fiber middleware (fiber.Handler, fasthttp-native)",
            python_counterpart="tornadoapi-guard",
            counterpart_rationale=(
                "non-standard I/O model (fasthttp, not net/http), like the "
                "non-ASGI Tornado adapter"
            ),
            snippet_language="go",
            snippet=GO_FIBER_SNIPPET,
            notes=(
                "no release tag yet; pin a commit or track main; shims fiber.Ctx "
                "directly, buffers the full body, and takes the client identity "
                "from the fasthttp TCP peer IP"
            ),
        ),
    ],
    agent=AgentInfo(
        package="guard-agent-go",
        repo="https://github.com/rennf93/guard-agent-go",
        version="0.1.0",
        install="go get github.com/rennf93/guard-agent-go@main",
        release_status="untagged",
        semantics=(
            "buffered background agent with at-least-once delivery: per-kind "
            "buffers of 100, 30s flush interval or the 0.8 high watermark, "
            "drop/block/raise overflow, 429 Retry-After honored (60s default, "
            "300s cap), 413 recursive batch halving, permanent drop on "
            "400/404/422, circuit breaker after 5 failures in 60s, a final flush "
            "on Stop, and optional Redis persistence that fails open"
        ),
        integration=(
            "standalone: it does not depend on guard-core-go and no adapter "
            "forwards telemetry automatically, so call SendEvent/SendMetric from "
            "your handlers or middleware"
        ),
        snippet_language="go",
        snippet=GO_AGENT_SNIPPET,
        notes=(
            "package name is guardagent; version 0.1.0 comes from the Version "
            "constant, there is no tag yet; SigningSecret signs the uncompressed "
            "body; install identity persists at ~/.guard-agent/install-id"
        ),
    ),
)

TS_EXPRESS_SNIPPET = """import express from 'express';
import { createSecurityMiddleware } from '@guardcore/express';

const app = express();

app.use(createSecurityMiddleware({
  config: {
    enableRateLimiting: true,
    rateLimit: 100,
    rateLimitWindow: 60,
    blockedUserAgents: ['badbot', 'scrapy'],
    enablePenetrationDetection: true,
  },
}));

app.listen(3000);"""

TS_FASTIFY_SNIPPET = """import Fastify from 'fastify';
import { guardPlugin } from '@guardcore/fastify';

const app = Fastify();

app.register(guardPlugin, {
  config: {
    enableRateLimiting: true,
    rateLimit: 100,
    rateLimitWindow: 60,
  },
});

app.listen({ port: 3000 });"""

TS_HONO_SNIPPET = """import { Hono } from 'hono';
import { createGuardMiddleware } from '@guardcore/hono';

const app = new Hono();

app.use('*', createGuardMiddleware({
  config: {
    enableRateLimiting: true,
    rateLimit: 100,
  },
}));

export default app;"""

TS_NESTJS_SNIPPET = """import { Module } from '@nestjs/common';
import { GuardModule } from '@guardcore/nestjs';

@Module({
  imports: [
    GuardModule.forRoot({
      config: {
        enableRateLimiting: true,
        rateLimit: 100,
      },
    }),
  ],
})
export class AppModule {}"""

TS_AGENT_SNIPPET = """import { GuardAgent, AgentConfig } from "guardagent";

const agent = new GuardAgent(AgentConfig.create({
  endpoint: "https://api.guard-core.com",
  apiKey: process.env.GUARD_API_KEY!,
  projectId: "my-project",
}));
await agent.start();

agent.sendEvent({ kind: "security_event", payload: { /* ... */ } });

await agent.stop(); // final flush + confirm"""

TS_ADAPTER_NOTES = (
    "pnpm monorepo (packages/*); adapters depend on @guardcore/core via "
    "workspace:* locally; release tag 1.0.0"
)


def _ts_adapter(package: str, framework: str, role: str, snippet: str) -> AdapterInfo:
    return AdapterInfo(
        package=package,
        repo=f"https://github.com/rennf93/guard-core-ts/tree/master/packages/{framework}",
        version="1.0.0",
        install=f"npm install @guardcore/core {package}",
        release_status="tagged",
        framework=framework,
        role=role,
        python_counterpart="fastapi-guard",
        counterpart_rationale=(
            "async middleware over an async framework, matching the ASGI adapter"
        ),
        snippet_language="typescript",
        snippet=snippet,
        notes=TS_ADAPTER_NOTES,
    )


TS_ENTRY = LanguageEntry(
    language="typescript",
    label="TypeScript",
    engine=EngineInfo(
        package="@guardcore/core",
        repo="https://github.com/rennf93/guard-core-ts",
        version="1.0.0",
        install="npm install @guardcore/core",
        release_status="tagged",
        conformance=(
            "spec-4.0.3 corpus vendored at conformance/guard-core-spec-4.0.3 "
            "(184 cases across 12 suites) with a fail-closed baseline whose "
            "expected-failure list is empty"
        ),
        notes=(
            "root package guardcore-ts is private and never published; the five "
            "packages publish to npm in lock-step on GitHub Release tags; config "
            "is a Zod SecurityConfigSchema parsed into the resolved config"
        ),
    ),
    adapters=[
        _ts_adapter(
            "@guardcore/express",
            "express",
            "Express middleware (app.use)",
            TS_EXPRESS_SNIPPET,
        ),
        _ts_adapter(
            "@guardcore/fastify",
            "fastify",
            "Fastify plugin (app.register)",
            TS_FASTIFY_SNIPPET,
        ),
        _ts_adapter(
            "@guardcore/hono",
            "hono",
            "Hono middleware (app.use('*'))",
            TS_HONO_SNIPPET,
        ),
        _ts_adapter(
            "@guardcore/nestjs",
            "nestjs",
            "NestJS module (GuardModule.forRoot)",
            TS_NESTJS_SNIPPET,
        ),
    ],
    agent=AgentInfo(
        package="guardagent",
        repo="https://github.com/rennf93/guard-agent-ts",
        version="0.1.0",
        install="pnpm add guardagent",
        release_status="untagged",
        semantics=(
            "1:1 port of the Python agent semantics: buffer of 100 per kind, "
            "30s flush interval, 0.8 high watermark, drop/block/raise overflow, "
            "Retry-After-aware backoff, 413 split-or-drop, permanent-rejection "
            "handling, optional ioredis crash recovery, gzip above 1024 bytes"
        ),
        integration=(
            "standalone package; the adapters do not wire it up for you, but "
            "@guardcore/core exposes sendAgentEvent and an agentHandler hook on "
            "initializeSecurityMiddleware for forwarding events"
        ),
        snippet_language="typescript",
        snippet=TS_AGENT_SNIPPET,
        notes=(
            "Node >= 20; signs the uncompressed body so signatures survive the "
            "server decompressing first; no git tag yet, so the npm publish must "
            "have run for pnpm add to resolve"
        ),
    ),
)

PHP_PSR15_SNIPPET = r"""use Nyholm\Psr7\Factory\Psr17Factory;
use RenzoFranceschini\GuardCore\Config\SecurityConfig;
use RenzoFranceschini\GuardCore\Engine\GuardEngine;
use RenzoFranceschini\GuardCorePsr15\GuardMiddleware;

$config = new SecurityConfig(
    enableRedis: false,
    blacklist: ['192.0.2.0/24'],
    rateLimit: 100,
    rateLimitWindow: 60,
    enableRateLimiting: true,
);

$factory = new Psr17Factory();
$engine = new GuardEngine($config);
$guard = new GuardMiddleware($engine, $factory, $factory);

$app->add($guard);"""

PHP_LARAVEL_SNIPPET = r"""use Illuminate\Http\Request;
use RenzoFranceschini\GuardCore\Config\SecurityConfig;
use RenzoFranceschini\GuardCore\Engine\GuardEngine;
use RenzoFranceschini\GuardCoreLaravel\GuardMiddleware;

// In a service provider (or any container binding)
$this->app->bind(GuardMiddleware::class, function () {
    $config = new SecurityConfig(
        enableRedis: false,
        blacklist: ['192.0.2.0/24'],
        rateLimit: 100,
        rateLimitWindow: 60,
        enableRateLimiting: true,
    );

    return new GuardMiddleware(new GuardEngine($config));
});

// Laravel 11/12, bootstrap/app.php
->withMiddleware(function (Middleware $middleware) {
    $middleware->prepend(GuardMiddleware::class);
});

// Laravel 10, app/Http/Kernel.php
protected $middleware = [
    // ...
    \RenzoFranceschini\GuardCoreLaravel\GuardMiddleware::class,
];"""

PHP_SYMFONY_SNIPPET = r"""use RenzoFranceschini\GuardCore\Config\SecurityConfig;
use RenzoFranceschini\GuardCore\Engine\GuardEngine;
use RenzoFranceschini\GuardCoreSymfony\GuardMiddleware;
use Symfony\Component\HttpFoundation\Request;

// Anywhere your App\Kernel is created
$kernel = new GuardMiddleware(
    new App\Kernel($_SERVER['APP_ENV'], (bool) $_SERVER['APP_DEBUG']),
    new GuardEngine(new SecurityConfig(
        enableRedis: false,
        blacklist: ['192.0.2.0/24'],
        rateLimit: 100,
        rateLimitWindow: 60,
        enableRateLimiting: true,
    ))
);

// public/index.php
$request = Request::createFromGlobals();
$response = $kernel->handle($request);
$response->send();
$kernel->terminate($request, $response);"""

PHP_SLIM_SNIPPET = r"""use RenzoFranceschini\GuardCore\Config\SecurityConfig;
use RenzoFranceschini\GuardCore\Engine\GuardEngine;
use RenzoFranceschini\GuardCoreSlim\SlimGuard;
use Slim\Factory\AppFactory;

$app = AppFactory::create();

SlimGuard::forApp($app, new GuardEngine(new SecurityConfig(
    enableRedis: false,
    blacklist: ['192.0.2.0/24'],
    rateLimit: 100,
    rateLimitWindow: 60,
    enableRateLimiting: true,
)))->addTo($app);"""

PHP_AGENT_SNIPPET = r"""use RenzoFranceschini\GuardAgent\Config\AgentConfigResolver;
use RenzoFranceschini\GuardAgent\GuardAgent;

$agent = new GuardAgent(AgentConfigResolver::resolve([
    'apiKey' => $_ENV['GUARD_API_KEY'],
    'endpoint' => 'https://api.guard-core.com',
    'projectId' => 'my-project',
    'payloadSigningSecret' => $_ENV['GUARD_SIGNING_SECRET'] ?? null,
]));

$agent->start();

// From anywhere in your request path: never throws, never blocks (default drop policy).
$agent->sendEvent([
    'event_type' => 'penetration_attempt',
    'ip_address' => $clientIp,
    'endpoint' => '/login',
    'method' => 'POST',
    'metadata' => ['rule' => 'sqli-union-select'],
]);

// Ship telemetry at the end of the request (kernel.terminate in Symfony,
// register_shutdown_function in plain PHP, terminate in Laravel).
register_shutdown_function(static function () use ($agent): void {
    $agent->flushBuffer();
    $agent->stop();
});"""

PHP_ENGINE_NOTES = (
    "composer rennf93/guard-core-php, php ^8.2 plus ext-pcre, ext-mbstring and "
    "ext-json; tag v0.1.0 is not on Packagist yet, so composer.json needs a VCS "
    "repository pointing at https://github.com/rennf93/guard-core-php with "
    "minimum-stability dev and prefer-stable true; namespace root "
    r"RenzoFranceschini\GuardCore"
)

PHP_ADAPTER_NOTES = (
    "php ^8.2; requires rennf93/guard-core-php ^0.1.0, which still needs the "
    "VCS repositories block until the engine reaches Packagist"
)


def _php_adapter(
    package: str,
    framework: str,
    version: str,
    role: str,
    counterpart: str,
    rationale: str,
    snippet: str,
    notes: str,
) -> AdapterInfo:
    return AdapterInfo(
        package=package,
        repo=f"https://github.com/rennf93/{package}",
        version=version,
        install=f"composer require {package}",
        release_status="tagged" if version != "unreleased" else "untagged",
        framework=framework,
        role=role,
        python_counterpart=counterpart,
        counterpart_rationale=rationale,
        snippet_language="php",
        snippet=snippet,
        notes=notes,
    )


PHP_ENTRY = LanguageEntry(
    language="php",
    label="PHP",
    engine=EngineInfo(
        package="guard-core-php",
        repo="https://github.com/rennf93/guard-core-php",
        version="0.1.0",
        install="composer require rennf93/guard-core-php",
        release_status="tagged",
        conformance=(
            "the composer conformance script (bin/conformance.php) runs the "
            "vendored spec-4.0.3 corpus (184 cases across 12 suites)"
        ),
        notes=PHP_ENGINE_NOTES,
    ),
    adapters=[
        _php_adapter(
            "psr15-guard",
            "psr15",
            "0.1.0",
            r"PSR-15 middleware (Psr\Http\Server\MiddlewareInterface)",
            "flaskapi-guard",
            "sync PSR-7 middleware, matching the sync-mirror extension style",
            PHP_PSR15_SNIPPET,
            PHP_ADAPTER_NOTES
            + "; tagged v0.1.0; needs a PSR-7/PSR-17 implementation such as "
            "nyholm/psr7; caps scanned bodies at MAX_BODY_BYTES (256 KiB)",
        ),
        _php_adapter(
            "laravel-guard",
            "laravel",
            "unreleased",
            "global Laravel middleware (prepend or $middleware stack)",
            "djapi-guard",
            "global framework middleware in a batteries-included MVC framework",
            PHP_LARAVEL_SNIPPET,
            PHP_ADAPTER_NOTES + "; no tags yet, installs from source (dev-main)",
        ),
        _php_adapter(
            "symfony-guard",
            "symfony",
            "unreleased",
            "HttpKernelInterface decorator (kernel middleware)",
            "djapi-guard",
            "kernel middleware stack wrapping the framework kernel",
            PHP_SYMFONY_SNIPPET,
            PHP_ADAPTER_NOTES
            + "; no tags yet, installs from source (dev-main); wraps the kernel "
            "rather than registering a bundle",
        ),
        _php_adapter(
            "slim-guard",
            "slim",
            "unreleased",
            "Slim App middleware (SlimGuard::forApp()->addTo())",
            "flaskapi-guard",
            "micro-framework integration over PSR-15 middleware",
            PHP_SLIM_SNIPPET,
            PHP_ADAPTER_NOTES
            + "; no tags yet, installs from source (dev-main); composes "
            "rennf93/psr15-guard ^0.1.0 rather than the engine directly",
        ),
    ],
    agent=AgentInfo(
        package="guard-agent-php",
        repo="https://github.com/rennf93/guard-agent-php",
        version="0.1.0",
        install="composer require rennf93/guard-agent-php",
        release_status="untagged",
        semantics=(
            "zero-dependency agent (ext-json and ext-curl only): buffer of 100, "
            "30s flush interval, tick() loop for long-running workers, "
            "drop-overflow by default so sendEvent never throws or blocks, "
            "optional Redis via ext-redis, predis or a built-in stream client "
            "with keys under {prefix}:agent_events and a 3600s TTL, gzip above "
            "1024 bytes"
        ),
        integration=(
            "standalone: no PHP adapter forwards telemetry automatically, so "
            "flush on request shutdown (register_shutdown_function, "
            "kernel.terminate or Laravel terminate) or run tick() in workers"
        ),
        snippet_language="php",
        snippet=PHP_AGENT_SNIPPET,
        notes=(
            "version 0.1.0 lives in the Version constant because composer.json "
            "carries no version field; no tags yet; signs the uncompressed body"
        ),
    ),
)

RUST_TOWER_SNIPPET = r"""use tower::Layer;

let layer = tower_guard_rs::GuardLayer::new(tower_guard_rs::default_config());

// Any `Service<Request<B>>` works; `axum::Router` is the usual one.
let service = layer.layer(my_service);"""

RUST_AXUM_SNIPPET = r"""use axum::Router;

let app = Router::new()
    .route("/", axum::routing::get(|| async { "hello" }))
    .layer(axum_guard_rs::with_guard(axum_guard_rs::default_config()));"""

RUST_ACTIX_SNIPPET = r"""use actix_guard_rs::{default_config, GuardTransform};
use actix_web::{App, HttpServer};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .wrap(GuardTransform::new(default_config()))
            .route("/", actix_web::web::to(|| async { "ok" }))
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}"""

RUST_ROCKET_SNIPPET = r"""use rocket::{get, post, routes};
use rocket_guard_rs::{BlockGuard, GuardBody, GuardFairing, default_config};

#[get("/health")]
fn health(_guard: BlockGuard) -> &'static str {
    "ok"
}

#[post("/submit", data = "<body>")]
fn submit(body: GuardBody) -> Vec<u8> {
    body.into_inner()
}

#[rocket::launch]
fn rocket() -> _ {
    rocket::build()
        .attach(GuardFairing::new(default_config()))
        .mount("/", routes![health, submit])
}"""

RUST_AGENT_SNIPPET = r"""use guard_agent_rs::{AgentConfig, GuardAgent, SecurityEvent};

#[tokio::main]
async fn main() {
    let mut config = AgentConfig::new("your-api-key-at-least-10-chars");
    config.endpoint = "https://api.guard-core.com".to_owned();
    config.project_id = Some("proj_your-project".to_owned());
    config.payload_signing_secret = Some("server-provided-signing-secret".to_owned());

    let agent = GuardAgent::new(config).expect("valid configuration");
    agent.start().await;

    agent
        .send_event(
            SecurityEvent::new("rate_limited")
                .with_ip_address("10.0.0.1")
                .with_endpoint("/api/users")
                .with_action_taken("blocked"),
        )
        .await;

    // ... at shutdown:
    agent.stop().await;
}"""

RUST_ENGINE_NOTES = (
    "cargo workspace (crates/*), edition 2024, MSRV 1.92; the engine crate "
    "guard-core-engine is publish = false and nothing is on crates.io yet, so "
    "adapters depend on it by path; the facade crate guard-core-rs re-exports "
    "only preprocessor and semantic, so adapters use guard-core-engine directly"
)

RUST_ADAPTER_NOTES = (
    "edition 2024, MSRV 1.92; fail-secure (500 on check failure), 403 for "
    "suspicious requests, 413 for oversized payloads; body cap configurable "
    "with with_body_cap; not on crates.io, path dependency until tagging"
)


def _rust_adapter(
    package: str,
    framework: str,
    role: str,
    counterpart: str,
    rationale: str,
    snippet: str,
    extra_notes: str = "",
) -> AdapterInfo:
    return AdapterInfo(
        package=package,
        repo=f"https://github.com/rennf93/{package}",
        version="0.1.0",
        install=f'{package} = {{ path = "../{package}" }}',
        release_status="untagged",
        framework=framework,
        role=role,
        python_counterpart=counterpart,
        counterpart_rationale=rationale,
        snippet_language="rust",
        snippet=snippet,
        notes=RUST_ADAPTER_NOTES + extra_notes,
    )


RUST_ENTRY = LanguageEntry(
    language="rust",
    label="Rust",
    engine=EngineInfo(
        package="guard-core-rs",
        repo="https://github.com/rennf93/guard-core-rs",
        version="0.0.1",
        install=(
            'guard-core-engine = { path = "../guard-core-rs/crates/guard-core-engine" }'
        ),
        release_status="untagged",
        conformance=(
            "spec-4.0.3 corpus vendored in the guard-core-conformance crate: "
            "184/184 cases green with a fail-closed drift gate and the "
            "pattern ledger recording the structural-match residuals"
        ),
        notes=RUST_ENGINE_NOTES,
    ),
    adapters=[
        _rust_adapter(
            "tower-guard-rs",
            "tower",
            "Tower Layer/Service (GuardLayer over http::Request)",
            "fastapi-guard",
            "async service layer, the closest analogue to an ASGI middleware",
            RUST_TOWER_SNIPPET,
        ),
        _rust_adapter(
            "axum-guard-rs",
            "axum",
            "axum Router layer (with_guard into Router::layer)",
            "fastapi-guard",
            "async service layer, the closest analogue to an ASGI middleware",
            RUST_AXUM_SNIPPET,
            "; depends on tower-guard-rs, which transitively carries the engine",
        ),
        _rust_adapter(
            "actix-guard-rs",
            "actix",
            "actix-web middleware (GuardTransform via App::wrap)",
            "tornadoapi-guard",
            "actor-model framework outside the ASGI standard",
            RUST_ACTIX_SNIPPET,
        ),
        _rust_adapter(
            "rocket-guard-rs",
            "rocket",
            "Rocket fairing (GuardFairing::attach) with BlockGuard and GuardBody",
            "tornadoapi-guard",
            "framework-native integration outside the ASGI standard",
            RUST_ROCKET_SNIPPET,
        ),
    ],
    agent=AgentInfo(
        package="guard-agent-rs",
        repo="https://github.com/rennf93/guard-agent-rs",
        version="0.1.0",
        install="cargo add guard-agent-rs",
        release_status="untagged",
        semantics=(
            "tokio-based async agent: per-kind buffers of 100, 30s flush "
            "interval, 0.8 high watermark, drop/block/raise overflow, "
            "Retry-After-aware backoff, gzip above 1024 bytes, optional Redis "
            "behind the persistence feature, install id persisted at "
            "~/.guard-agent/install-id"
        ),
        integration=(
            "standalone crate (no dependency on the engine); call send_event "
            "from your handlers and stop() at shutdown for the final flush"
        ),
        snippet_language="rust",
        snippet=RUST_AGENT_SNIPPET,
        notes=(
            "no git tag yet, so confirm the crates.io release exists before "
            "relying on cargo add; use --features persistence for Redis; signs "
            "the uncompressed body"
        ),
    ),
)

PY_FASTAPI_SNIPPET = """from fastapi import FastAPI
from guard import SecurityMiddleware, SecurityConfig

app = FastAPI()

config = SecurityConfig(
    enable_rate_limiting=True,
    rate_limit=100,
    rate_limit_window=60,
    enable_ip_banning=True,
    auto_ban_threshold=5,
    auto_ban_duration=86400,
    custom_log_file="security.log",
    enforce_https=True,
    enable_cors=True,
    cors_allow_origins=["*"],
    cors_allow_methods=["GET", "POST"],
    cors_allow_headers=["*"],
    cors_allow_credentials=True,
    cors_expose_headers=["X-Custom-Header"],
    cors_max_age=600,
    block_cloud_providers={"AWS", "GCP", "Azure"},
)

app.add_middleware(SecurityMiddleware, config=config)"""

PY_FLASK_SNIPPET = """from flaskapi_guard import FlaskAPIGuard, SecurityConfig

config = SecurityConfig(fail_secure=False)
FlaskAPIGuard(app, config=config)"""

PY_DJANGO_SNIPPET = """from djangoapi_guard import SecurityConfig

GUARD_SECURITY_CONFIG = SecurityConfig(
    fail_secure=False,
)"""

PY_TORNADO_SNIPPET = """from tornadoapi_guard import SecurityConfig, SecurityMiddleware

config = SecurityConfig(
    fail_secure=False,
)
middleware = SecurityMiddleware(config=config)"""

PY_AGENT_SNIPPET = """import os

from guard import SecurityConfig, SecurityDecorator, SecurityMiddleware

api_key = os.environ.get("GUARD_API_KEY", "")
project_id = os.environ.get("GUARD_PROJECT_ID", "")
core_url = os.environ.get("GUARD_CORE_URL", "https://api.guard-core.com")

security_config = SecurityConfig(
    auto_ban_threshold=5,
    auto_ban_duration=300,
    enable_agent=bool(api_key),
    agent_api_key=api_key,
    agent_endpoint=core_url,
    agent_project_id=project_id,
    agent_buffer_size=100,
    agent_flush_interval=2,
    enable_dynamic_rules=bool(api_key),
    dynamic_rule_interval=60,
)

app.add_middleware(SecurityMiddleware, config=security_config)
SecurityMiddleware.configure_cors(app, security_config)
app.state.guard_decorator = SecurityDecorator(security_config)"""


def _python_adapter(
    package: str,
    framework: str,
    version: str,
    role: str,
    snippet: str,
) -> AdapterInfo:
    return AdapterInfo(
        package=package,
        repo=f"https://github.com/rennf93/{package}",
        version=version,
        install=f"uv add {package}",
        release_status="published",
        framework=framework,
        role=role,
        python_counterpart=package,
        counterpart_rationale="this is the Python adapter other languages map to",
        snippet_language="python",
        snippet=snippet,
        notes="the other three Python adapters mirror this one over guard_core.sync",
    )


PY_ENTRY = LanguageEntry(
    language="python",
    label="Python",
    engine=EngineInfo(
        package="guard-core",
        repo="https://github.com/rennf93/guard-core",
        version="4.0.4",
        install="uv add guard-core",
        release_status="published",
        conformance=(
            "reference implementation: the spec-4.0.3 fixture corpus was "
            "generated from its enhanced 4.x detection path"
        ),
        notes=(
            "import name guard_core; the async tree is the authored source and "
            "guard_core.sync is the unasync-generated mirror for sync adapters; "
            "introspect it live with the validate_config and config_fields tools"
        ),
    ),
    adapters=[
        _python_adapter(
            "fastapi-guard",
            "fastapi",
            "8.0.0",
            "ASGI middleware for FastAPI (async tree)",
            PY_FASTAPI_SNIPPET,
        ),
        _python_adapter(
            "flaskapi-guard",
            "flask",
            "4.3.0",
            "Flask extension over the sync mirror",
            PY_FLASK_SNIPPET,
        ),
        _python_adapter(
            "djangoapi-guard",
            "django",
            "4.3.0",
            "Django middleware adapter over the sync mirror",
            PY_DJANGO_SNIPPET,
        ),
        _python_adapter(
            "tornadoapi-guard",
            "tornado",
            "1.0.0",
            "Tornado handler/middleware adapter (async tree)",
            PY_TORNADO_SNIPPET,
        ),
    ],
    agent=AgentInfo(
        package="guard-agent",
        repo="https://github.com/rennf93/guard-agent",
        version="3.0.1",
        install="uv add guard-agent",
        release_status="published",
        semantics=(
            "async buffering agent: per-kind buffers of 100 (agent_buffer_size), "
            "flush every 30s or at the 0.8 high watermark, drop/block/raise "
            "overflow, gzip above 1024 bytes, Retry-After-aware backoff, "
            "permanent drop on 400/404/422, 413 split-or-drop, optional Redis "
            "crash recovery, and optional AES-256-GCM payload encryption"
        ),
        integration=(
            "the adapters integrate it through guard-core's handler initializer: "
            "enable it with enable_agent plus agent_api_key, agent_endpoint and "
            "agent_project_id on SecurityConfig"
        ),
        snippet_language="python",
        snippet=PY_AGENT_SNIPPET,
        notes=(
            "3.0.1 signs the compressed wire bytes when the body exceeds the "
            "compression threshold, while the server verifies the uncompressed "
            "body, so see the saas.known_quirks entry before enabling "
            "require_signed_payloads"
        ),
    ),
)

REGISTRY = EcosystemRegistry(
    languages={
        "python": PY_ENTRY,
        "go": GO_ENTRY,
        "typescript": TS_ENTRY,
        "php": PHP_ENTRY,
        "rust": RUST_ENTRY,
    },
    conformance=ConformanceInfo(
        reference="guard-core (Python), the enhanced 4.x detection path",
        spec_version="4.0.3",
        cases=184,
        suites=12,
        engine_commit="436d6f72",
        corpus=(
            "every engine vendors the same frozen spec-4.0.3 fixture corpus: "
            "xss 22, sqli 22, cmd_injection 18, misc_injection 29, "
            "inclusion_sensitive_recon 18, path_traversal 10, context_matrix 9, "
            "benign 15, encoding 8, boundaries 8, semantic 6, "
            "binary_bodies 19"
        ),
        interop=(
            "82/82 cases pass in the cross-language Redis interop harness "
            "(Python reference, Go and PHP ports sharing one Redis), plus "
            "24/24 Redis-free binary-body detect vectors per engine port"
        ),
    ),
    saas=SaaSContract(
        base_url="https://api.guard-core.com",
        endpoints={
            "POST /api/v1/events": "batch security events",
            "POST /api/v1/metrics": "batch metrics; doubles as the heartbeat",
            "POST /api/v1/status": "agent status beacon",
            "GET /api/v1/status": "agent-facing status probe",
            "POST /api/v1/events/encrypted": (
                "AES-256-GCM envelope variant used when the Python agent "
                "carries a project_encryption_key"
            ),
        },
        headers={
            "X-API-Key": "required",
            "X-Project-Id": "optional project scoping",
            "X-Agent-Install-Id": (
                "optional; honored when install-id tracking is enabled server-side"
            ),
            "X-Payload-Signature": (
                "optional; 'v1=' plus lowercase hex HMAC-SHA256 over the "
                "UNCOMPRESSED body (the server decompresses gzip before verifying)"
            ),
            "Content-Encoding": "gzip when the body is compressed",
        },
        signing=(
            "HMAC-SHA256 over the uncompressed JSON body, prefixed v1= and "
            "hex-encoded in X-Payload-Signature; the server's gzip middleware "
            "decompresses first, so signing compressed wire bytes fails verification"
        ),
        compression=(
            "gzip above the 1024-byte compression threshold by default; the "
            "payload size limit is enforced against the decompressed body"
        ),
        limits={
            "max_decompressed_bytes": (
                "262144 (256 KiB, INGEST_MAX_PAYLOAD_BYTES); over the cap "
                "returns 413, a missing Content-Length returns 411"
            ),
            "agent_compression_threshold": "1024 bytes",
            "agent_max_payload_size": "1024 bytes per event payload (agent-side)",
        },
        response_semantics={
            "200": (
                "accepted; a body with success=false or errors means a partial "
                "failure: agents requeue the batch in memory, retain the Redis "
                "keys and back off"
            ),
            "429": (
                "rate limited (per-IP, per-API-key and per-project token "
                "buckets); agents must honor Retry-After (capped at 300s "
                "client-side) and retry rather than drop"
            ),
            "413": (
                "payload too large; agents split the batch in half recursively "
                "or drop the singleton"
            ),
            "400/404/422": (
                "permanent rejections; agents drop the batch and never retry"
            ),
            "401/403": "authentication and IP-allowlist failures",
            "503": (
                "transient server contention or a tripped circuit breaker; "
                "carries Retry-After"
            ),
        },
        known_quirks=[
            (
                "guard-agent 3.0.1 (Python) still signs the compressed wire bytes once "
                "the body exceeds the compression threshold while the server "
                "verifies the uncompressed body, so signed and gzipped batches "
                "from that release fail verification when require_signed_payloads "
                "is enabled"
            ),
            (
                "the Go, TypeScript, PHP and Rust agents sign the uncompressed "
                "body and match the server contract"
            ),
        ],
    ),
)


def ecosystem() -> dict[str, Any]:
    return REGISTRY.model_dump()


def _find_language(language: str) -> LanguageEntry | None:
    return REGISTRY.languages.get(language.strip().lower())


def _find_adapter(entry: LanguageEntry, framework: str) -> AdapterInfo | None:
    needle = framework.strip().lower()
    for adapter in entry.adapters:
        if needle in (adapter.framework, adapter.package.lower()):
            return adapter
    return None


def _unknown_language_error(language: str) -> dict[str, str]:
    return {
        "error": (
            f"unknown language {language!r}; expected one of "
            f"{', '.join(REGISTRY.languages)}"
        )
    }


def _unknown_framework_error(entry: LanguageEntry, framework: str) -> dict[str, str]:
    return {
        "error": (
            f"unknown framework {framework!r} for {entry.label}; adapters: "
            f"{', '.join(adapter.framework for adapter in entry.adapters)}"
        )
    }


def adapter_setup(language: str, framework: str) -> dict[str, Any]:
    entry = _find_language(language)
    if entry is None:
        return _unknown_language_error(language)
    adapter = _find_adapter(entry, framework)
    if adapter is None:
        return _unknown_framework_error(entry, framework)
    return {
        "language": entry.language,
        "engine": {
            "package": entry.engine.package,
            "install": entry.engine.install,
            "release_status": entry.engine.release_status,
            "conformance": entry.engine.conformance,
        },
        "adapter": adapter.model_dump(),
    }


def wire_agent(language: str, framework: str | None = None) -> dict[str, Any]:
    entry = _find_language(language)
    if entry is None:
        return _unknown_language_error(language)
    note = entry.agent.integration
    if framework is not None:
        adapter = _find_adapter(entry, framework)
        if adapter is None:
            return _unknown_framework_error(entry, framework)
        if entry.language == "python":
            note = (
                f"{note}; the bundled guard-agent docs cover this adapter at "
                f"adapters/{adapter.framework}.md (get_doc package='guard-agent')"
            )
        else:
            note = (
                f"{note}; the {adapter.framework} adapter adds no agent wiring of "
                "its own beyond this"
            )
    return {
        "language": entry.language,
        "agent": entry.agent.model_dump(),
        "ingestion": REGISTRY.saas.model_dump(),
        "framework_note": note,
    }
