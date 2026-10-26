---
name: rate-limits-abuse
description: Add and verify rate limiting and abuse controls on login, signup, reset, OTP, search, costly and AI endpoints. Use when endpoints can be brute-forced, scraped, spammed or used to run up cost.
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Rate Limits Abuse

## Objective

Bound request volume and cost per identity and per source, and fail safely.

## When to Use

Use when: endpoints can be brute-forced, scraped, spammed or used to run up cost.

Do not use for: Business-rule abuse (payment-business-logic).

## Scope

Edge/proxy limits, application middleware, shared stores, CAPTCHA/challenge integration.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Choose keys (account, IP, token), windows and shared storage.
4. Return 429 with Retry-After; monitor hits.
5. Decide fail-open vs fail-closed deliberately; default closed for auth.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- List sensitive endpoints and current limits.
- Test limits in a non-production environment with safe volumes.
- Check bypass: header spoofing, multiple instances, per-IP only.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-28 — Missing or ineffective rate limits

- **Detect:** Check login, reset, signup, OTP, search, expensive and AI endpoints for throttling; check keying (IP only vs account) and bypass via headers.
- **Fix:** Apply per-account and per-IP limits with a shared store; stricter limits on auth and costly endpoints; return 429 with Retry-After.
- **Verify:** Load test within safe limits on a test environment to confirm 429 occurs and limits survive multiple instances.
- **Also involves:** `authentication-authorization`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-04` Weak authentication (owner: `authentication-authorization`)
- `SEC-24` Broken password reset flows (owner: `authentication-authorization`)
- `SEC-56` Account enumeration (owner: `authentication-authorization`)
- `SEC-57` Business logic abuse (owner: `payment-business-logic`)
- `SEC-63` Security checks that fail open (owner: `security-audit`)
- `SEC-64` Missing timeouts (owner: `ssrf-cors-webhooks`)
- `UX-03` Site search (owner: `website-interactions`)
- `PROD-18` Spam protection (owner: `forms-validation`)

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

- IP-based limits are weak behind shared NAT and trivial for distributed attackers.
- Real DDoS protection happens at provider/edge level, not in app code.
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

- `authentication-authorization`
- `payment-business-logic`
- `logging-monitoring-backups`
