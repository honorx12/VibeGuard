---
name: session-jwt-oauth
description: 'Review sessions, JWTs and OAuth/OIDC: weak session management, weak or exposed JWT secrets and validation, and misconfigured OAuth. Use when implementing or auditing login sessions, token issuance or social login.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Session JWT, OAuth

## Objective

Ensure tokens and sessions are generated, validated, stored, rotated and revoked correctly.

## When to Use

Use when: implementing or auditing login sessions, token issuance or social login.

Do not use for: Password flows and MFA (authentication-authorization).

## Scope

Session middleware, token libraries, OAuth client/server config, cookie and storage handling.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Pin algorithms; validate exp/iss/aud; short lifetimes; rotation.
4. Regenerate session IDs on login; invalidate on logout.
5. Exact-match redirect URIs, state and PKCE.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Read token verification code.
- Tamper tests (alg none, wrong audience, expired).
- OAuth flow review: redirect URI, state, PKCE, scopes.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-25 — Weak session management

- **Detect:** Review session ID generation, rotation on login, idle/absolute timeout, logout invalidation and storage.
- **Fix:** Use framework session management; regenerate ID on privilege change; enforce timeouts; server-side invalidate on logout.
- **Verify:** Tests: session fixation attempt fails; logout invalidates server-side; expired sessions rejected.
- **Also involves:** `web-input-security`

### SEC-26 — Exposed or weak JWT secrets and validation

- **Detect:** Check secret strength/location, algorithm pinning, alg=none handling, exp/aud/iss validation, key rotation and token storage.
- **Fix:** Use strong secrets or asymmetric keys from a secret manager; pin allowed algorithms; validate exp, iss, aud; keep access tokens short-lived.
- **Verify:** Tests: tampered, unsigned, expired, wrong-audience and wrong-algorithm tokens are rejected.
- **Also involves:** `secrets-detection`

### SEC-54 — Misconfigured OAuth

- **Detect:** Review redirect URI validation, state/nonce, PKCE, scope minimisation, token storage, account linking.
- **Fix:** Exact-match redirect URIs; require state and PKCE; least scopes; verify ID token claims; safe account linking.
- **Verify:** Tests: altered redirect URI, missing state and replayed codes are rejected.
- **Also involves:** `web-input-security`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-20` Cross-site request forgery (CSRF) (owner: `web-input-security`)
- `SEC-47` Insecure cookie settings (owner: `web-input-security`)
- `SEC-55` Missing MFA (owner: `authentication-authorization`)
- `SEC-68` Sensitive browser storage (owner: `web-input-security`)
- `SEC-69` Open redirects (owner: `web-input-security`)

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

- Identity-provider side settings must be reviewed in the provider console by a human.
- Library defaults change between versions; check the version in use.
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
- `web-input-security`
- `secrets-detection`
