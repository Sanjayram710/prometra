# Security Policy

Prometra takes the security and privacy of developer data very seriously. Because Prometra is built from the ground up to be **100% local-first**, your code, session metrics, AI prompts, and database files never leave your local machine.

---

## Supported Versions

We actively support security updates for the following release versions of Prometra:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.9.x   | :white_check_mark: |
| < 1.9   | :x:                |

---

## Reporting a Vulnerability

If you discover a security vulnerability or potential privacy issue in Prometra, please do **NOT** open a public issue on GitHub.

Instead, please report vulnerabilities directly to our security maintainers:

- **Email**: `security@prometra.dev`
- **GPG Key**: Available upon request.

### What to Include in Your Report

1. Description of the vulnerability and its potential impact.
2. Steps to reproduce the issue (including sample code or CLI commands).
3. Component(s) affected (e.g. SQLite storage layer, Smart Ignore rules, Connector SDK).
4. Proposed mitigation or patch if available.

### Response Timeline

- **Acknowledgement**: Within 24 hours.
- **Triage & Assessment**: Within 72 hours.
- **Fix & Patch Release**: Security patches will be prioritized and released within 7 business days.

---

## Local Privacy Guarantees

Prometra operates under strict architectural security principles:

- **No Remote Telemetry**: Prometra does not collect analytics or phone home.
- **Local SQLite Engine**: All data is stored in standard, un-encrypted or user-managed `.prometra/prometra.db` files inside your repository root.
- **Zero Cloud APIs**: No third-party network APIs or external web services are invoked by Prometra's core tracking or diff engines.
