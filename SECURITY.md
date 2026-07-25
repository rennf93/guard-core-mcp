# Security Policy for Guard Core MCP

## Supported Versions

Guard Core MCP is pre-1.0. We provide security updates for the latest published release only:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

Once the project reaches 1.0, this table will track supported major versions the same way the rest of the Guard ecosystem does.

## Reporting a Vulnerability

We take the security of Guard Core MCP seriously. If you believe you've found a security vulnerability, please follow these steps:

1. **Do not disclose the vulnerability publicly** until it has been addressed by the maintainers.
2. **Report the vulnerability through GitHub's security advisory feature**:
   - Go to the [Security tab](https://github.com/rennf93/guard-core-mcp/security/advisories) of the Guard Core MCP repository
   - Click on "New draft security advisory"
   - Fill in the details of the vulnerability
   - Submit the advisory

   Alternatively, you can report vulnerabilities through [GitHub's private vulnerability reporting feature](https://github.com/rennf93/guard-core-mcp/security/advisories/new).

3. Include the following information in your report:
   - A description of the vulnerability and its potential impact
   - Steps to reproduce the issue
   - Affected versions
   - Any potential mitigations or workarounds

The maintainers will acknowledge your report within 48 hours and provide a detailed response within 7 days, including the next steps in handling the vulnerability.

## Security Best Practices

Guard Core MCP is a local [MCP](https://modelcontextprotocol.io) server: it runs inside your own project's Python environment and answers an AI coding agent's questions by introspecting the Guard libraries actually installed there. When using it, consider the following:

### Install target

1. **Install it into your project's environment, not an isolated one.** `uvx guard-core-mcp` will start, but an isolated environment has no `guard-core`, `fastapi-guard`, or `guard-agent` for it to introspect, so every answer falls back to bundled documentation rather than your actual installed versions. Prefer `uv add --dev guard-core-mcp` inside the project whose Guard configuration you want checked.
2. **Do not point it at an environment holding production credentials it does not need.** The server only reads package metadata and executes the detection engine against synthetic, in-memory requests — it makes no network calls and opens no ports — but it inherits whatever the hosting environment can see, so keep it scoped to development and CI environments.

### Tool call inputs

1. **`check_payload` runs its input through guard-core's real detection engine, not a sandboxed copy of it.** The regex protections (bounded quantifiers, per-pattern timeouts) are the same ones guard-core ships in production, so pathological input is handled the same way it would be at your application's edge — but treat payloads passed through your MCP client the same way you'd treat any other tool argument: avoid pasting real user data or secrets into a debugging session, since your MCP client may log tool calls.
2. **`check_payload` always forces `enable_redis=False`** on the `SecurityConfig` it builds, regardless of what a caller passes in `config`. This is deliberate: it prevents a tool call from causing the server to open a connection to a Redis instance the caller specifies. There is no equivalent override for other outbound-network-capable `SecurityConfig` fields (e.g. a custom `geo_ip_handler`), so avoid passing configuration that points at infrastructure you don't control.
3. **`validate_config` and `config_fields` instantiate the real Pydantic model** (`SecurityConfig` / `AgentConfig`) from whichever Guard package you ask about. Pydantic validation does not execute arbitrary code from its input, but as with any tool, only pass configuration you intend to test.

### Dependency management

1. Regularly update Guard Core MCP and the Guard libraries it introspects (`guard-core`, `fastapi-guard`, `guard-agent`) to the latest versions.
2. Use a dependency scanning tool to identify and address vulnerabilities in your dependency tree.

## Security Features

Guard Core MCP provides several properties that make it safer to run than an AI agent guessing from memory:

- Answers about a Guard library's configuration come from the **real, installed Pydantic model**, not from training data that may be stale or version-mismatched.
- `check_payload` exercises the **real detection engine**, so "would this be blocked" answers reflect actual behavior rather than a plausible-sounding guess.
- No outbound network calls, no listening ports, and no persistence — the server only reads local package metadata, local bundled documentation, and processes synthetic in-memory requests.
- Redis is unconditionally disabled for the detection sandbox, regardless of caller-supplied configuration.
- Failure paths degrade to a structured error (`missing_library_error`) rather than raising, so a Guard library missing from the host environment cannot crash the server or leak a stack trace to the calling agent.

## Threat Model

Guard Core MCP is not a network-facing service and does not itself protect an application from anything — that is the job of `fastapi-guard` / `guard-core` / `guard-agent`, which it introspects. Its own threat model is narrower:

- **Supply-chain integrity**: install Guard Core MCP from PyPI with your usual dependency-pinning and provenance practices, the same way you would any other developer tool with access to your project's environment.
- **Tool-output trust**: like any MCP tool, its output is text an AI agent may act on. Treat a `check_payload` verdict as evidence for a decision, not as the decision itself, particularly for security-relevant changes.
- **Local environment exposure**: because it runs inside your project's environment, anything that environment can reach is technically reachable by code the server imports (`guard-core`, `fastapi-guard`, `guard-agent`, and their dependencies). This is standard for any developer tool installed via `uv add --dev` and is why we recommend scoping it to development and CI environments.

## Security Updates

Security updates will be released as needed. We recommend subscribing to GitHub releases or regularly checking for updates to ensure you're using the most secure version.

## Responsible Disclosure

We follow responsible disclosure principles. If you report a vulnerability to us:

1. We will confirm receipt of your vulnerability report
2. We will provide an estimated timeline for a fix
3. We will notify you when the vulnerability is fixed
4. We will publicly acknowledge your responsible disclosure (unless you prefer to remain anonymous)

## License

Guard Core MCP is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
