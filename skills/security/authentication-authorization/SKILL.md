---
name: authentication-authorization
description: 'Review and fix authentication and authorization: weak login, missing authz checks, admin routes, password reset, default credentials, MFA, account enumeration and client-only security. Use when building or auditing login, roles, admin areas or account recovery.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Authentication Authorization

## Objective

Ensure identity is verified robustly and every action is authorised on the server.

## When to Use

Use when: building or auditing login, roles, admin areas or account recovery.

Do not use for: Session/JWT/OAuth internals (session-jwt-oauth); object-level checks (api-access-control).

## Scope

Login, signup, reset, MFA, role/permission logic, admin and internal routes, seeds and default accounts.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Prefer maintained auth libraries or identity providers over custom crypto.
4. Deny by default; centralise policy.
5. Test each protected route as anonymous, wrong role, right role.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Route-by-route authn/authz matrix.
- Read auth middleware and policy code.
- Behavioural tests with anonymous, user and admin identities.
- Response and timing comparison for enumeration.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-04 — Weak authentication

- **Detect:** Review password policy, hashing algorithm, login flow, lockout, and any custom auth code that replaces a vetted library.
- **Fix:** Use a maintained auth library or identity provider; hash with Argon2id, scrypt or bcrypt; enforce length-based policy and breach-password checks.
- **Verify:** Unit/integration tests for hashing parameters, lockout/throttle behaviour and rejection of weak passwords.
- **Also involves:** `rate-limits-abuse`

### SEC-05 — Missing authorization checks

- **Detect:** Enumerate every route/handler/action and mark which check identity and which check permission; look for handlers with no check.
- **Fix:** Enforce authorization server-side, deny by default, centralise policy in middleware or policy functions.
- **Verify:** Per-endpoint tests: anonymous, wrong-role and correct-role requests return 401/403/200 as designed.
- **Also involves:** `api-access-control`

### SEC-09 — Unprotected admin routes

- **Detect:** List admin/internal routes (/admin, /internal, /debug, framework admin panels) and test them unauthenticated and as a normal user.
- **Fix:** Require authentication plus an admin role check on every admin route; restrict by network or VPN where possible; require MFA for admins.
- **Verify:** Automated test that anonymous and non-admin requests to each admin route are rejected.
- **Also involves:** `cloud-config`

### SEC-15 — Client-only security

- **Detect:** Find checks that exist only in UI code (hidden buttons, client-side role flags, JS validation, price calculations).
- **Fix:** Re-implement every check on the server; treat client state as untrusted input.
- **Verify:** Bypass the UI (curl or API client) and confirm the server still rejects the forbidden action.
- **Also involves:** `payment-business-logic`, `web-input-security`

### SEC-24 — Broken password reset flows

- **Detect:** Review token generation, expiry, single use, storage, delivery, host-header trust and session invalidation after reset.
- **Fix:** Use high-entropy single-use tokens stored hashed, short expiry, constant responses regardless of account existence, invalidate sessions after reset.
- **Verify:** Tests: reused, expired and tampered tokens fail; response identical for known/unknown emails; old sessions revoked.
- **Also involves:** `rate-limits-abuse`

### SEC-30 — Default credentials

- **Detect:** Search seeds, docker-compose, README, IaC and admin tools for admin/admin, changeme, example passwords.
- **Fix:** Remove defaults; require first-run credential setup; generate random secrets per environment.
- **Verify:** Attempt documented default logins against a test deployment and confirm failure; seed scripts contain none.
- **Also involves:** `secrets-detection`

### SEC-55 — Missing MFA

- **Detect:** Check whether admins and sensitive accounts can enrol and are required to use MFA; check recovery paths.
- **Fix:** Offer TOTP/WebAuthn; require for privileged users; protect recovery flows; avoid SMS-only where feasible.
- **Verify:** Test that privileged login without second factor fails and recovery cannot bypass it.
- **Also involves:** `session-jwt-oauth`

### SEC-56 — Account enumeration

- **Detect:** Compare responses, status codes and timing for login, signup and reset with known vs unknown accounts.
- **Fix:** Use uniform messages and similar timing; rate limit; avoid confirming existence.
- **Verify:** Automated comparison of responses for existing vs non-existing accounts shows no distinguishable difference.
- **Also involves:** `rate-limits-abuse`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-06` Cross-user access (owner: `api-access-control`)
- `SEC-28` Missing or ineffective rate limits (owner: `rate-limits-abuse`)
- `SEC-33` IDOR / BOLA (owner: `api-access-control`)
- `SEC-45` Exposed internal dashboards (owner: `cloud-config`)
- `SEC-70` Unsecured endpoints (owner: `api-access-control`)
- `UX-13` Password visibility toggle (owner: `forms-validation`)

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

- Cannot detect business-specific permission intent without the owner's role model.
- Timing tests are noisy; treat results as indicators.
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

- `api-access-control`
- `session-jwt-oauth`
- `rate-limits-abuse`
- `secrets-detection`
