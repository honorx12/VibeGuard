---
name: crypto-data-protection
description: 'Protect sensitive data: unencrypted data in transit or at rest, password storage, key handling and sensitive information leakage through responses, URLs, caches and analytics. Use when handling PII, credentials, payments or health/financial data.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Crypto Data Protection

## Objective

Ensure sensitive data is minimised, encrypted appropriately and not leaked.

## When to Use

Use when: handling PII, credentials, payments or health/financial data.

Do not use for: Secrets in code (secrets-detection).

## Scope

TLS config, storage encryption, field-level encryption, key management, API response schemas, caching and analytics payloads.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Prefer vetted libraries and managed key services; no custom crypto.
4. Classify data and minimise collection.
5. Plan key rotation.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- TLS handshake checks against owned hosts.
- IaC/console flags for encryption.
- Response-schema inspection.
- Search for custom cryptography.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-48 — Unencrypted sensitive data

- **Detect:** Check TLS in transit (including internal), encryption at rest, field-level protection of sensitive data, password storage and key management.
- **Fix:** Enforce TLS; enable storage encryption; encrypt high-sensitivity fields with managed keys; hash passwords; plan key rotation.
- **Verify:** Verify TLS config with a scanner or handshake test; confirm encryption flags in IaC/console; inspect stored values for plaintext.
- **Also involves:** `cloud-config`

### SEC-65 — Sensitive information leakage

- **Detect:** Check API responses, errors, URLs, referrers, analytics, caches and exports for over-sharing of PII/secrets.
- **Fix:** Return minimal fields via explicit response schemas; keep secrets out of URLs; set cache-control on sensitive responses; scrub analytics.
- **Verify:** Response-schema tests assert absence of sensitive fields; inspect cache headers on sensitive routes.
- **Also involves:** `logging-monitoring-backups`, `web-input-security`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-49` Poor tenant isolation (owner: `api-access-control`)
- `PROD-04` Enforce HTTPS (owner: `production-readiness`)

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

- Compliance (GDPR, HIPAA, PCI DSS) needs qualified review; this skill does not certify compliance.
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
- `api-access-control`
