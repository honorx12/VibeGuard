---
name: ssrf-cors-webhooks
description: 'Secure outbound requests, cross-origin policy and webhooks: SSRF, permissive CORS, unsigned webhooks, webhook replay and missing timeouts. Use when code fetches user-supplied URLs, configures CORS, or receives provider webhooks.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# SSRF, CORS Webhooks

## Objective

Constrain where the server connects, who browsers may talk to, and which inbound events are trusted.

## When to Use

Use when: code fetches user-supplied URLs, configures CORS, or receives provider webhooks.

Do not use for: General injection (injection-prevention).

## Scope

HTTP clients, URL fetchers, CORS config, webhook endpoints, timeouts and retry settings.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Allowlist destinations; validate after DNS resolution and each redirect.
4. Verify signatures on raw body; add timestamp window and event-ID store.
5. Set explicit timeouts everywhere.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Find outbound request code paths with user input.
- Inspect CORS middleware config.
- Review webhook handlers for signature, timestamp, idempotency.
- Fault tests with slow or private-range targets.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-23 — Server-side request forgery (SSRF)

- **Detect:** Find server-side fetches of user-supplied URLs (previews, webhooks, importers, image proxies).
- **Fix:** Allowlist destinations; resolve DNS and block private, loopback, link-local and metadata ranges after redirects; disable or re-validate redirects; enforce timeouts and size limits.
- **Verify:** Tests against localhost, 169.254.169.254, private ranges, DNS-rebinding style hostnames and redirects to them are all blocked.
- **Also involves:** `cloud-config`

### SEC-27 — Permissive CORS

- **Detect:** Look for Access-Control-Allow-Origin: * with credentials, reflected Origin, overly broad regex origins, null origin.
- **Fix:** Allowlist exact origins; never combine wildcard with credentials; restrict methods and headers.
- **Verify:** Send requests with disallowed Origin headers and confirm no ACAO header; allowed origin returns exact match only.

### SEC-31 — Unsigned webhooks

- **Detect:** Check inbound webhook handlers for signature verification using the raw body and a constant-time comparison.
- **Fix:** Verify provider signature with the shared secret before processing; reject on failure; fail closed.
- **Verify:** Tests: missing, invalid and modified-body signatures are rejected; valid signature accepted.
- **Also involves:** `payment-business-logic`

### SEC-59 — Webhook replay

- **Detect:** Check for timestamp tolerance and event-ID de-duplication on inbound webhooks.
- **Fix:** Reject stale timestamps; store processed event IDs; make handlers idempotent.
- **Verify:** Replay a captured valid request and confirm it is rejected or has no second effect.
- **Also involves:** `payment-business-logic`

### SEC-64 — Missing timeouts

- **Detect:** Find outbound HTTP, DB, queue and subprocess calls without timeouts and servers without request/body limits.
- **Fix:** Set connect/read timeouts, retries with backoff and caps, request size limits, circuit breakers.
- **Verify:** Test against a slow endpoint confirms the call aborts within the configured limit.
- **Also involves:** `rate-limits-abuse`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-32` Frontend-only payment verification (owner: `payment-business-logic`)
- `SEC-63` Security checks that fail open (owner: `security-audit`)

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

- DNS rebinding and redirect chains need dynamic testing in a controlled setup.
- Provider-specific signature schemes must be checked in vendor docs.
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

- `payment-business-logic`
- `cloud-config`
- `rate-limits-abuse`
