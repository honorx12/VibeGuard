# VibeGuard

**Security, quality and launch-readiness skills for AI coding agents.**

[![License: MIT](https://img.shields.io/github/license/honorx12/VibeGuard)](LICENSE)
[![Stars](https://img.shields.io/github/stars/honorx12/VibeGuard?style=flat)](https://github.com/honorx12/VibeGuard/stargazers)

24 skills (`SKILL.md` files) that guide Claude Code, Cursor, Codex, Copilot, Gemini CLI and Windsurf to find, fix and *verify* problems in AI-generated and vibe-coded web apps: secrets, auth, injection, SSRF, payments, performance, SEO, accessibility and more.

**Quick start**

```bash
git clone https://github.com/honorx12/VibeGuard.git
# copy only the skill folders you need into your agent's skills folder
# Claude Code (project): .claude/skills/<name>/   (verify path, see agents/README.md)
```

Then ask your agent: *"Use security-audit on this project."*

---

> **Honest scope.** These skills guide an agent's workflow. They do not make a system secure, compliant or accessible. A passing checklist is not proof. Findings must be backed by evidence and verification, and some decisions need a human.

## What is inside

| Area | Skills |
| --- | --- |
| Security (15) | `security-audit` (orchestrator), `secrets-detection`, `authentication-authorization`, `api-access-control`, `injection-prevention`, `web-input-security`, `ssrf-cors-webhooks`, `session-jwt-oauth`, `rate-limits-abuse`, `cloud-config`, `logging-monitoring-backups`, `ai-agent-security`, `dependency-supply-chain`, `crypto-data-protection`, `payment-business-logic` |
| Frontend (4) | `accessibility-responsive`, `website-interactions`, `forms-validation`, `consent-and-privacy-ui` |
| Production (3) | `production-readiness`, `performance`, `seo-metadata` |
| Engineering (2) | `code-review-testing`, `skill-supply-chain-review` |

Coverage: **70 security issues**, **20 UX enhancements**, **20 production-checklist items plus 7 extensions**. Every item has a stable ID (`SEC-01`…, `UX-01`…, `PROD-01`…), a primary skill, and detect / fix / verify guidance. See [`docs/COVERAGE_MAP.md`](docs/COVERAGE_MAP.md) (generated) and `registry/coverage.json`.

## Install and use

```bash
python -m venv .venv && . .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt                  # exact tested versions: requirements-lock.txt
python scripts/validate_skills.py                    # validate skills, coverage, registry
python -m pytest                                     # run tests
python scripts/build_registry.py --check             # confirm generated files are current
python scripts/scan_project.py path/to/project       # candidate-only local scan (read-only, offline)
```

To use skills with an agent, copy only the skill folders you need into that agent's skills location. See [`agents/README.md`](agents/README.md): it separates what is confirmed from what must be checked against vendor documentation.

Start with `security-audit`, which routes to specialist skills based on your actual stack and defines the audit workflow (understand, select, audit, prioritise, plan, remediate, verify, report) and the approval gates for destructive, production, credential and permission changes.

## Tools

| Script | Purpose | Network |
| --- | --- | --- |
| `scripts/validate_skills.py` | Frontmatter (spec rules), required sections, duplicate names, local references, related skills, coverage and registry validation. Nonzero exit on failure. | none |
| `scripts/scan_project.py` | Inventory plus regex *candidates*. Never prints secret values, never modifies the target, skips dependency/build dirs. | none |
| `scripts/build_registry.py` | Builds `registry/skills-index.json` and `docs/COVERAGE_MAP.md`; `--check` detects stale output. | none |
| `scripts/discover_skills.py` | Catalogues public skills through the GitHub REST API (metadata only; optional heuristic inspection). Nothing is installed or executed. | GitHub API (optional `GITHUB_TOKEN`) |

## Third-party content and licensing

This repository is MIT licensed (see `LICENSE`). It contains **no copied third-party skills**. External skills are only catalogued (`registry/external-candidates.json`) with source URL, licence, revision and retrieval date; entries with unclear or restrictive licences are marked `link-only`. Every external entry requires human review before any adoption. See [`docs/DISCOVERY_PIPELINE.md`](docs/DISCOVERY_PIPELINE.md).

## Known limitations

- The local scanner is a small regex tool with false positives and false negatives (see `examples/example-audit-report.md` for a real miss).
- Per-agent install paths were gathered from third-party sources, not vendor docs, in this release; see `agents/README.md`.
- The first discovery run hit the unauthenticated GitHub rate limit; most candidates have unresolved revisions and no heuristic inspection (details in `docs/DISCOVERY_REPORT.md`).
- No CI workflow is shipped yet (see roadmap).
- Skills have not been evaluated empirically against agent behaviour. Only structure and traceability are tested.

## Roadmap

CI workflow with SHA-pinned actions; per-skill `references/` for long topics; agent behaviour evals; vendor-doc verification of integration paths; richer scanner rules with an allowlist file.

## Docs

[Architecture](docs/ARCHITECTURE.md) · [Operating model](docs/OPERATING_MODEL.md) · [Security model](docs/SECURITY_MODEL.md) · [Authoring guide](docs/SKILL_AUTHORING_GUIDE.md) · [Discovery pipeline](docs/DISCOVERY_PIPELINE.md) · [Contributing](CONTRIBUTING.md)
