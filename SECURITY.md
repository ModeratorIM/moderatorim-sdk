# Security Policy

`moderatorim-sdk` is the contract kernel of the ModeratorIM project. Security reporting and
disclosure follow the **project-wide policy** in the main repository:

➡️ **https://github.com/ModeratorIM/ModeratorIM/blob/main/SECURITY.md**

## Reporting a vulnerability

**Do not report vulnerabilities through public issues, pull requests, or discussions.** Report
privately using either:

- **GitHub Security Advisories** — the repository's **Security → Report a vulnerability** tab
  (preferred).
- **Email** — `security@moderatorim.com` <!-- TODO: confirm the real disclosure address -->

Never include real secrets, API keys, or personal member data in a report — use redacted or
synthetic examples.

## Scope note for this repository

This package is **contracts only** (declarations: models, the data-store port, the manifest, the
event bus, the routing facade) — it has no runtime, no network calls, and no data handling. Most
security-relevant behavior lives in the **core runtime**; report findings there per the policy
above. In scope here: a contract whose shape enables an unsafe pattern in every consumer (e.g. a
validation gap that lets a malformed declaration through). See the project policy for the full
supported-versions table and disclosure philosophy.
