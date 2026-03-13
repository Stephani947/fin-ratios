# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |
| < 1.0   | No        |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report security issues by emailing the maintainer directly or using [GitHub's private vulnerability reporting](https://github.com/piyushgupta344/fin-ratios/security/advisories/new).

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix if you have one

You will receive a response within **72 hours**. If the issue is confirmed, a patch will be released within **14 days** for critical issues.

## Scope

fin-ratios is a computation library with **zero runtime network dependencies in the core**. The attack surface is limited:

- **Core ratio functions**: Pure functions — no I/O, no network, no file access. No meaningful attack surface.
- **Fetchers** (`fetchers/` submodule): Makes outbound HTTP requests to third-party financial APIs. Vulnerabilities here could include SSRF if user-controlled URLs were accepted (they are not — tickers are used to construct known endpoint URLs).
- **REST API** (`api.py`): FastAPI server. Report any injection or authentication bypass issues.
- **MCP server** (`mcp_server.py`): Report any prompt injection or data exfiltration risks.
- **CLI**: Report any command injection issues.

## Dependency Updates

Dependencies are monitored via Dependabot. Critical dependency CVEs are patched as soon as a fix is available upstream.
