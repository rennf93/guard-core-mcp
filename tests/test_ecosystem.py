from guard_core_mcp import ecosystem as ecosystem_module
from guard_core_mcp.ecosystem import (
    REGISTRY,
    adapter_setup,
    ecosystem,
    wire_agent,
)

EXPECTED_LANGUAGES = {"python", "go", "typescript", "php", "rust"}

SNIPPET_API_NAMES = {
    "nethttp-guard": "nethttp.New(engine)",
    "gin-guard": "guardgin.New(engine)",
    "echo-guard": "guardecho.New(engine)",
    "fiber-guard": "guardfiber.New(engine)",
    "@guardcore/express": "createSecurityMiddleware",
    "@guardcore/fastify": "guardPlugin",
    "@guardcore/hono": "createGuardMiddleware",
    "@guardcore/nestjs": "GuardModule.forRoot",
    "psr15-guard": "GuardMiddleware($engine, $factory, $factory)",
    "laravel-guard": "GuardMiddleware::class",
    "symfony-guard": "new GuardMiddleware(",
    "slim-guard": "SlimGuard::forApp($app",
    "tower-guard-rs": "GuardLayer::new(",
    "axum-guard-rs": "with_guard(",
    "actix-guard-rs": "GuardTransform::new(",
    "rocket-guard-rs": "GuardFairing::new(",
    "fastapi-guard": "app.add_middleware(SecurityMiddleware, config=config)",
    "flaskapi-guard": "FlaskAPIGuard(app, config=config)",
    "djangoapi-guard": "GUARD_SECURITY_CONFIG",
    "tornadoapi-guard": "SecurityMiddleware(config=config)",
}

AGENT_SNIPPET_NAMES = {
    "go": "agent.SendEvent(ctx, guardagent.SecurityEvent{",
    "typescript": "AgentConfig.create({",
    "php": "AgentConfigResolver::resolve([",
    "rust": "AgentConfig::new(",
    "python": "agent_api_key=api_key",
}


def every_adapter():
    for entry in REGISTRY.languages.values():
        for adapter in entry.adapters:
            yield entry, adapter


def test_registry_covers_every_language_with_engine_adapters_and_agent() -> None:
    assert set(REGISTRY.languages) == EXPECTED_LANGUAGES
    for entry in REGISTRY.languages.values():
        assert entry.engine.package
        assert entry.agent.package
        assert len(entry.adapters) == 4


def test_every_package_declares_a_known_release_status() -> None:
    for entry in REGISTRY.languages.values():
        assert entry.engine.release_status in {"published", "tagged", "untagged"}
        assert entry.agent.release_status in {"published", "tagged", "untagged"}
        for _, adapter in every_adapter():
            assert adapter.release_status in {"published", "tagged", "untagged"}


def test_registry_maps_every_adapter_to_a_python_counterpart() -> None:
    for _entry, adapter in every_adapter():
        assert adapter.python_counterpart in {
            "fastapi-guard",
            "flaskapi-guard",
            "djapi-guard",
            "tornadoapi-guard",
            adapter.package,
        }
        assert adapter.counterpart_rationale
        assert adapter.role


def test_registry_records_the_go_engine_facts() -> None:
    go = REGISTRY.languages["go"]

    assert go.engine.package == "guard-core-go"
    assert go.engine.version == "0.1.0"
    assert go.engine.release_status == "tagged"
    assert go.engine.install == "go get github.com/rennf93/guard-core-go@v0.1.0"
    assert "184 cases" in go.engine.conformance

    assert {adapter.package for adapter in go.adapters} == {
        "nethttp-guard",
        "gin-guard",
        "echo-guard",
        "fiber-guard",
    }
    nethttp = go.adapters[0]
    assert nethttp.release_status == "tagged"
    assert "@v0.1.0" in nethttp.install
    for untagged in go.adapters[1:]:
        assert untagged.release_status == "untagged"
        assert "@main" in untagged.install

    assert go.agent.package == "guard-agent-go"
    assert go.agent.version == "0.1.0"
    assert go.agent.release_status == "untagged"
    assert go.agent.install == "go get github.com/rennf93/guard-agent-go@main"


def test_registry_records_the_typescript_engine_facts() -> None:
    ts = REGISTRY.languages["typescript"]

    assert ts.engine.package == "@guardcore/core"
    assert ts.engine.version == "1.0.0"
    assert ts.engine.release_status == "tagged"

    assert {adapter.package for adapter in ts.adapters} == {
        "@guardcore/express",
        "@guardcore/fastify",
        "@guardcore/hono",
        "@guardcore/nestjs",
    }
    for adapter in ts.adapters:
        assert adapter.version == "1.0.0"
        assert adapter.release_status == "tagged"
        assert adapter.install.startswith("npm install @guardcore/core")

    assert ts.agent.package == "guardagent"
    assert ts.agent.version == "0.1.0"
    assert ts.agent.release_status == "untagged"


def test_registry_records_the_php_engine_facts() -> None:
    php = REGISTRY.languages["php"]

    assert php.engine.package == "guard-core-php"
    assert php.engine.version == "0.1.0"
    assert php.engine.release_status == "tagged"
    assert "bin/conformance.php" in php.engine.conformance

    assert {adapter.package for adapter in php.adapters} == {
        "psr15-guard",
        "laravel-guard",
        "symfony-guard",
        "slim-guard",
    }
    psr15 = php.adapters[0]
    assert psr15.version == "0.1.0"
    assert psr15.release_status == "tagged"
    for untagged in php.adapters[1:]:
        assert untagged.release_status == "untagged"
        assert untagged.version == "unreleased"

    assert php.agent.package == "guard-agent-php"
    assert php.agent.release_status == "untagged"


def test_registry_records_the_rust_engine_facts() -> None:
    rust = REGISTRY.languages["rust"]

    assert rust.engine.package == "guard-core-rs"
    assert rust.engine.version == "0.0.1"
    assert rust.engine.release_status == "untagged"
    assert "guard-core-engine" in rust.engine.install
    assert "184/184 cases green" in rust.engine.conformance

    assert {adapter.package for adapter in rust.adapters} == {
        "tower-guard-rs",
        "axum-guard-rs",
        "actix-guard-rs",
        "rocket-guard-rs",
    }
    for adapter in rust.adapters:
        assert adapter.version == "0.1.0"
        assert adapter.release_status == "untagged"
        assert 'path = "../' in adapter.install

    assert rust.agent.package == "guard-agent-rs"
    assert rust.agent.version == "0.1.0"
    assert rust.agent.release_status == "untagged"


def test_registry_records_the_python_engine_facts() -> None:
    python = REGISTRY.languages["python"]

    assert python.engine.package == "guard-core"
    assert python.engine.version == "4.0.4"
    assert python.engine.release_status == "published"

    versions = {adapter.package: adapter.version for adapter in python.adapters}
    assert versions == {
        "fastapi-guard": "8.0.0",
        "flaskapi-guard": "4.3.0",
        "djangoapi-guard": "4.3.0",
        "tornadoapi-guard": "1.0.0",
    }

    assert python.agent.package == "guard-agent"
    assert python.agent.version == "3.0.1"
    assert python.agent.release_status == "published"


def test_conformance_block_pins_the_frozen_corpus() -> None:
    conformance = REGISTRY.conformance

    assert conformance.spec_version == "4.0.3"
    assert conformance.cases == 184
    assert conformance.suites == 12
    assert conformance.engine_commit == "436d6f72"
    assert "82/82" in conformance.interop
    assert "xss 22" in conformance.corpus
    assert conformance.reference.startswith("guard-core (Python)")


def test_saas_block_documents_the_ingestion_contract() -> None:
    saas = REGISTRY.saas

    assert saas.base_url == "https://api.guard-core.com"
    assert {
        "POST /api/v1/events",
        "POST /api/v1/metrics",
        "POST /api/v1/status",
    } <= set(saas.endpoints)
    assert saas.headers["X-API-Key"] == "required"
    assert "UNCOMPRESSED" in saas.headers["X-Payload-Signature"]
    assert "uncompressed" in saas.signing
    assert "262144" in saas.limits["max_decompressed_bytes"]
    assert "partial failure" in saas.response_semantics["200"]
    assert "Retry-After" in saas.response_semantics["429"]
    assert "permanent" in saas.response_semantics["400/404/422"]
    assert any("guard-agent 3.0.1" in quirk for quirk in saas.known_quirks)


def test_every_adapter_snippet_carries_its_verified_api_name() -> None:
    for _, adapter in every_adapter():
        assert SNIPPET_API_NAMES[adapter.package] in adapter.snippet
        assert adapter.snippet_language


def test_every_agent_snippet_carries_its_verified_api_name() -> None:
    for entry in REGISTRY.languages.values():
        assert AGENT_SNIPPET_NAMES[entry.language] in entry.agent.snippet
        assert entry.agent.semantics
        assert entry.agent.integration


def test_ecosystem_returns_the_registry_dump() -> None:
    assert ecosystem() == REGISTRY.model_dump()


def test_adapter_setup_returns_the_adapter_and_its_engine() -> None:
    result = adapter_setup("go", "gin")

    assert result["adapter"]["package"] == "gin-guard"
    assert result["adapter"]["framework"] == "gin"
    assert result["engine"]["package"] == "guard-core-go"
    assert "guard-core-go@v0.1.0" in result["engine"]["install"]


def test_adapter_setup_accepts_the_adapter_package_name() -> None:
    result = adapter_setup("typescript", "@guardcore/express")

    assert result["adapter"]["package"] == "@guardcore/express"


def test_adapter_setup_tolerates_case_and_whitespace() -> None:
    assert adapter_setup(" PHP ", "LARAVEL ")["adapter"]["package"] == "laravel-guard"


def test_adapter_setup_reports_an_unknown_language() -> None:
    result = adapter_setup("haskell", "axum")

    assert "unknown language 'haskell'" in result["error"]
    assert "python" in result["error"]


def test_adapter_setup_reports_an_unknown_framework() -> None:
    result = adapter_setup("go", "fastapi")

    assert "unknown framework 'fastapi'" in result["error"]
    assert "nethttp" in result["error"]


def test_wire_agent_returns_the_agent_and_the_ingestion_contract() -> None:
    result = wire_agent("go")

    assert result["language"] == "go"
    assert result["agent"]["package"] == "guard-agent-go"
    assert result["ingestion"]["base_url"] == "https://api.guard-core.com"
    assert result["framework_note"] == REGISTRY.languages["go"].agent.integration


def test_wire_agent_with_a_framework_names_the_adapter() -> None:
    result = wire_agent("go", "fiber")

    assert "fiber" in result["framework_note"]


def test_wire_agent_for_python_points_at_the_bundled_doc_page() -> None:
    result = wire_agent("python", "fastapi")

    assert "adapters/fastapi.md" in result["framework_note"]
    assert "get_doc" in result["framework_note"]


def test_wire_agent_reports_an_unknown_language() -> None:
    assert "unknown language 'elixir'" in wire_agent("elixir")["error"]


def test_wire_agent_reports_an_unknown_framework() -> None:
    result = wire_agent("rust", "rocket2")

    assert "unknown framework 'rocket2'" in result["error"]
    assert "tower" in result["error"]


def test_ecosystem_module_exposes_the_registry_for_the_server() -> None:
    assert ecosystem_module.REGISTRY is REGISTRY
