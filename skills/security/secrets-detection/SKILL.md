---
name: secrets-detection
description: 'Find and remediate exposed credentials: hardcoded secrets, public .env files, secrets in Git history, frontend bundles and logs, and exposed database credentials. Use when reviewing config, preparing a release, or after a suspected leak.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Secrets Detection

## Objective

Locate credential exposure, confirm it with evidence, rotate and relocate secrets, and verify no exposure remains.

## When to Use

Use when: reviewing config, preparing a release, or after a suspected leak.

Do not use for: General vulnerability review (use security-audit); license or PII compliance scanning.

## Scope

Working tree, Git history, build output, container contexts, CI config, logs and public web paths of a test deployment.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Treat any exposed secret as compromised: rotate first (human approval), then clean up.
4. Never paste real secret values into reports, tickets or prompts; reference file and line only.
5. Add .gitignore/.dockerignore entries and a pre-commit or CI secret scan.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Dedicated scanners where installed (gitleaks, trufflehog, detect-secrets); run them locally, never upload code.
- `python scripts/scan_project.py` for candidate patterns; values are never printed.
- Inspect production build output and public env prefixes.
- Review logging statements and sample log output.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-01 — Exposed database credentials

- **Detect:** Search config, code, CI files, container images and history for connection strings with embedded passwords; check whether the DB port is reachable from the public internet.
- **Fix:** Move credentials to a secret manager or runtime environment; rotate any exposed credential (human approval); restrict DB network access.
- **Verify:** Re-scan working tree and history; confirm the old credential no longer authenticates; confirm DB port unreachable from outside the allowed network.
- **Also involves:** `cloud-config`

### SEC-02 — Public .env files

- **Detect:** Check that .env* is git-ignored and absent from build output, Docker contexts and web roots; request /.env on a deployed test host.
- **Fix:** Add .env* to .gitignore and .dockerignore; keep only a placeholder .env.example; configure the web server to deny dotfiles.
- **Verify:** Fetch /.env and variants against the deployed build: expect 403/404 and no secret content. Confirm `git ls-files` lists no real .env.
- **Also involves:** `cloud-config`

### SEC-03 — Hardcoded secrets

- **Detect:** Run a dedicated secret scanner (e.g. gitleaks, trufflehog, detect-secrets) plus entropy and keyword review of source, tests, notebooks and IaC.
- **Fix:** Replace literals with environment or secret-manager lookups; fail fast at startup when a required secret is missing; rotate exposed values.
- **Verify:** Scanner reports zero verified findings (document allowlisted false positives); app fails clearly when a secret is unset.

### SEC-11 — Secrets in logs

- **Detect:** Search logging calls for request bodies, headers, tokens, connection strings, and objects serialized whole; inspect sample logs.
- **Fix:** Add redaction in the logger (authorization, cookie, password, token, key fields); log identifiers not payloads.
- **Verify:** Test that a request containing a canary secret never appears in captured log output.
- **Also involves:** `logging-monitoring-backups`

### SEC-13 — Secrets in Git history

- **Detect:** Scan full history and all branches/tags (e.g. gitleaks/trufflehog in git mode), including deleted files.
- **Fix:** Rotate the secret first (human approval). History rewriting is optional, destructive and needs explicit approval; deletion from HEAD alone is not a fix.
- **Verify:** History scan shows no active secrets; the exposed credential is confirmed revoked.

### SEC-14 — Secrets in frontend JavaScript

- **Detect:** Inspect built bundles, HTML, source maps and public env prefixes (NEXT_PUBLIC_, VITE_, REACT_APP_) for private keys or privileged tokens.
- **Fix:** Move privileged calls to a backend; only publishable/public keys may reach the client; rotate leaked keys.
- **Verify:** Grep production build output for known secret patterns and key names; confirm the client works using only public keys.
- **Also involves:** `web-input-security`

### PROD-03 — Remove frontend secrets

- **Detect:** Scan bundles and public env prefixes.
- **Fix:** Move privileged operations to the server; rotate leaked keys.
- **Verify:** Production build scan clean; see SEC-14.
- **Also involves:** `production-readiness`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-26` Exposed or weak JWT secrets and validation (owner: `session-jwt-oauth`)
- `SEC-30` Default credentials (owner: `authentication-authorization`)
- `SEC-36` Exposed source maps (owner: `cloud-config`)

## Remediation

- Apply the smallest change that removes the confirmed problem; keep public behaviour stable.
- Prefer maintained libraries and platform features over custom implementations.
- Require human approval before: destructive changes, credential rotation, production deployment, external side effects, or material cloud permission changes.
- Add or update an automated regression test for each fix where practical.

## Verification

- Run the **Verify** step for every item touched; record the exact command and observed result.
- Run the project's existing tests, linter, type checker and build.
- Re-run the relevant scanner or check after the fix and compare with the baseline.
- Report any check that could not run as **unverified**, with the reason. Never report a pass for a check that did not execute.
- A passing checklist does not show the system is secure; state residual risk.

## Limitations

- Pattern and entropy scans produce false positives and negatives.
- Rewriting Git history is destructive and does not revoke leaked secrets.
- Cannot confirm a credential is revoked without the owner testing it.
- Findings that depend on business intent, legal interpretation or production state need human review.

## Output Format

Report each finding as:

```text
ID: <coverage ID>   Severity: <Critical|High|Medium|Low|Info>   Confidence: <confirmed|likely|possible>
Location: <file:line or URL path>
Evidence: <command output or request/response excerpt; secrets redacted>
Impact: <what an attacker or user could do>
Fix: <change made or proposed>
Verification: <command run and result, or 'unverified: reason'>
```

End with: commands executed, checks skipped or unavailable, residual risks, and items needing human decision.

## Related Skills

- `cloud-config`
- `logging-monitoring-backups`
- `dependency-supply-chain`
