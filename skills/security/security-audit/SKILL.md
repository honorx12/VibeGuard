---
name: security-audit
description: 'Orchestrate an evidence-based security audit of a web app, API or AI-powered project: map trust boundaries, select specialist skills, rank findings, plan fixes, verify and report. Use when asked to audit, harden or review security of a codebase, or before launch. Also covers unreviewed code and fail-open checks.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Security Audit

## Objective

Run a repeatable audit workflow that selects the right specialist skills, separates confirmed findings from suspicions, and produces a prioritised, verified report.

## When to Use

Use when: asked to audit, harden or review security of a codebase, or before launch. Also covers unreviewed code and fail-open checks.

Do not use for: Single-topic questions already covered by a specialist skill (load that skill directly); penetration testing against systems you are not authorised to test.

## Scope

Application source, configuration, IaC, CI/CD files and (with approval) a non-production deployment. Production access and credential rotation need explicit human approval.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Inventory: language, framework, dependencies, DB, auth model, deployment target, test commands.
4. Select skills from the routing table below based on the actual stack; do not load everything.
5. Collect evidence per finding: file path, line, command output, request/response.
6. Rank by severity, exploitability, exposure, confidence and business impact.
7. Present a plan (changes, expected effect, tests, breaking risks) before risky operations.
8. Remediate in small focused commits; avoid unrelated rewrites.
9. Verify with real commands; record outputs. Never write 'passes' for a check that did not run.
10. Report findings, changes, commands run, outcomes, residual risk, unavailable checks.
11. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
12. Rank by severity, exploitability, exposure, confidence and business impact.
13. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
14. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
15. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Run `python scripts/scan_project.py <target>` for a conservative inventory (candidates only).
- Run ecosystem tools that exist in the project (dependency audit, linters, type checks, tests).
- Manual trace of trust boundaries: who can call what, with which identity, touching which data.
- Read route/handler lists and authorization code paths directly.

### Routing Table

| Area | Skill |
| --- | --- |
| Secrets and credentials | `secrets-detection` |
| Authentication, admin, MFA, recovery | `authentication-authorization` |
| Object-level access, tenancy, endpoints | `api-access-control` |
| Injection and input validation | `injection-prevention` |
| Browser and HTTP security | `web-input-security` |
| SSRF, CORS, webhooks | `ssrf-cors-webhooks` |
| Sessions, JWT, OAuth | `session-jwt-oauth` |
| Abuse and rate limiting | `rate-limits-abuse` |
| Cloud and deployment config | `cloud-config` |
| Logging, monitoring, backups | `logging-monitoring-backups` |
| AI features and agents | `ai-agent-security` |
| Dependencies and CI/CD | `dependency-supply-chain` |
| Encryption and data protection | `crypto-data-protection` |
| Payments and business logic | `payment-business-logic` |
| Reviewing code changes | `code-review-testing` |
| Third-party skills | `skill-supply-chain-review` |

### Severity Rubric

| Severity | Meaning |
| --- | --- |
| Critical | Remotely exploitable now with severe impact (e.g. live credential exposure, auth bypass on sensitive data). |
| High | Exploitable with modest effort or exposes significant data or functions. |
| Medium | Needs specific conditions or limited impact; defence-in-depth gaps. |
| Low | Minor weakness or hardening opportunity. |
| Info | Observation with no direct risk. |

State confidence (confirmed, likely, possible) separately from severity.

### Full Issue Index

- `SEC-01` Exposed database credentials → `secrets-detection`
- `SEC-02` Public .env files → `secrets-detection`
- `SEC-03` Hardcoded secrets → `secrets-detection`
- `SEC-04` Weak authentication → `authentication-authorization`
- `SEC-05` Missing authorization checks → `authentication-authorization`
- `SEC-06` Cross-user access → `api-access-control`
- `SEC-07` Open database permissions → `cloud-config`
- `SEC-08` Cloud service misconfiguration → `cloud-config`
- `SEC-09` Unprotected admin routes → `authentication-authorization`
- `SEC-10` Exposed production debug tools → `cloud-config`
- `SEC-11` Secrets in logs → `secrets-detection`
- `SEC-12` Verbose production errors → `cloud-config`
- `SEC-13` Secrets in Git history → `secrets-detection`
- `SEC-14` Secrets in frontend JavaScript → `secrets-detection`
- `SEC-15` Client-only security → `authentication-authorization`
- `SEC-16` Missing or weak input validation → `injection-prevention`
- `SEC-17` SQL injection → `injection-prevention`
- `SEC-18` NoSQL injection → `injection-prevention`
- `SEC-19` Cross-site scripting (XSS) → `web-input-security`
- `SEC-20` Cross-site request forgery (CSRF) → `web-input-security`
- `SEC-21` Insecure file uploads → `web-input-security`
- `SEC-22` Path traversal → `injection-prevention`
- `SEC-23` Server-side request forgery (SSRF) → `ssrf-cors-webhooks`
- `SEC-24` Broken password reset flows → `authentication-authorization`
- `SEC-25` Weak session management → `session-jwt-oauth`
- `SEC-26` Exposed or weak JWT secrets and validation → `session-jwt-oauth`
- `SEC-27` Permissive CORS → `ssrf-cors-webhooks`
- `SEC-28` Missing or ineffective rate limits → `rate-limits-abuse`
- `SEC-29` Exposed development and staging environments → `cloud-config`
- `SEC-30` Default credentials → `authentication-authorization`
- `SEC-31` Unsigned webhooks → `ssrf-cors-webhooks`
- `SEC-32` Frontend-only payment verification → `payment-business-logic`
- `SEC-33` IDOR / BOLA → `api-access-control`
- `SEC-34` Unsafe APIs accepting untrusted input → `api-access-control`
- `SEC-35` Exposed logs → `cloud-config`
- `SEC-36` Exposed source maps → `cloud-config`
- `SEC-37` Vulnerable dependencies → `dependency-supply-chain`
- `SEC-38` Malicious packages → `dependency-supply-chain`
- `SEC-39` Prompt injection → `ai-agent-security`
- `SEC-40` Unpermissioned AI access → `ai-agent-security`
- `SEC-41` Excessive database permissions → `cloud-config`
- `SEC-42` Missing audit logs → `logging-monitoring-backups`
- `SEC-43` Missing security monitoring → `logging-monitoring-backups`
- `SEC-44` Missing or untested backups → `logging-monitoring-backups`
- `SEC-45` Exposed internal dashboards → `cloud-config`
- `SEC-46` Missing security headers → `web-input-security`
- `SEC-47` Insecure cookie settings → `web-input-security`
- `SEC-48` Unencrypted sensitive data → `crypto-data-protection`
- `SEC-49` Poor tenant isolation → `api-access-control`
- `SEC-50` Unreviewed code → `security-audit`
- `SEC-51` Mass assignment → `api-access-control`
- `SEC-52` Command injection → `injection-prevention`
- `SEC-53` Insecure deserialization → `injection-prevention`
- `SEC-54` Misconfigured OAuth → `session-jwt-oauth`
- `SEC-55` Missing MFA → `authentication-authorization`
- `SEC-56` Account enumeration → `authentication-authorization`
- `SEC-57` Business logic abuse → `payment-business-logic`
- `SEC-58` Race conditions → `payment-business-logic`
- `SEC-59` Webhook replay → `ssrf-cors-webhooks`
- `SEC-60` Insecure CI/CD → `dependency-supply-chain`
- `SEC-61` Untrusted build actions → `dependency-supply-chain`
- `SEC-62` Unpinned build dependencies → `dependency-supply-chain`
- `SEC-63` Security checks that fail open → `security-audit`
- `SEC-64` Missing timeouts → `ssrf-cors-webhooks`
- `SEC-65` Sensitive information leakage → `crypto-data-protection`
- `SEC-66` Invalid AI output → `ai-agent-security`
- `SEC-67` Excessive AI permissions → `ai-agent-security`
- `SEC-68` Sensitive browser storage → `web-input-security`
- `SEC-69` Open redirects → `web-input-security`
- `SEC-70` Unsecured endpoints → `api-access-control`

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-50 — Unreviewed code

- **Detect:** Check branch protection, required reviews, review of AI-generated code, and CODEOWNERS for sensitive paths.
- **Fix:** Require human review before merge, especially for AI-generated changes and security-sensitive paths.
- **Verify:** Confirm protection settings in the platform and that recent merges had reviews.
- **Also involves:** `code-review-testing`

### SEC-63 — Security checks that fail open

- **Detect:** Search for try/except that allows access on error, auth/rate-limit/WAF clients that default to allow on timeout, scanners marked non-blocking.
- **Fix:** Fail closed for auth, authorisation, validation and signature checks; alert on check failures.
- **Verify:** Fault-injection tests: when the check dependency is down, the protected action is denied.
- **Also involves:** `rate-limits-abuse`, `ssrf-cors-webhooks`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-60` Insecure CI/CD (owner: `dependency-supply-chain`)
- `SEC-67` Excessive AI permissions (owner: `ai-agent-security`)

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

- A completed checklist never proves a system is secure.
- Static review misses runtime and configuration issues; dynamic testing needs an authorised test environment.
- Requires human approval for destructive changes, production deployments, credential rotation, external side effects and material cloud permission changes.
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

- `secrets-detection`
- `authentication-authorization`
- `api-access-control`
- `injection-prevention`
- `web-input-security`
- `ssrf-cors-webhooks`
- `session-jwt-oauth`
- `rate-limits-abuse`
- `cloud-config`
- `logging-monitoring-backups`
- `ai-agent-security`
- `dependency-supply-chain`
- `crypto-data-protection`
- `payment-business-logic`
- `code-review-testing`
