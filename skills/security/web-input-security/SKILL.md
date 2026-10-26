---
name: web-input-security
description: 'Secure the browser-facing surface: XSS, CSRF, file uploads, security headers, cookie flags, sensitive browser storage and open redirects. Use when building or auditing pages, forms, uploads, cookies or redirect logic.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Web Input Security

## Objective

Ensure untrusted data cannot execute in the browser and browser protections are enabled and verified.

## When to Use

Use when: building or auditing pages, forms, uploads, cookies or redirect logic.

Do not use for: Server-side injection (injection-prevention); JWT/session logic (session-jwt-oauth).

## Scope

Templates, frontend components, response headers, Set-Cookie, upload handlers, redirect handlers, browser storage.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Prefer framework escaping; sanitise rich content with a maintained library.
4. Introduce CSP in report-only mode, then enforce.
5. Verify headers in the deployed environment, not only in code.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Grep for dangerous sinks (innerHTML, dangerouslySetInnerHTML, v-html).
- `curl -I` on a production-like build.
- Browser devtools storage and cookie inspection.
- Payload tests in every user-content field.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-19 — Cross-site scripting (XSS)

- **Detect:** Find innerHTML, dangerouslySetInnerHTML, v-html, unescaped template output, unsafe URL attributes, and markdown/HTML rendering of user content.
- **Fix:** Use context-aware output encoding; prefer framework auto-escaping; sanitise rich HTML with a maintained sanitizer; add a Content-Security-Policy.
- **Verify:** Inject test payloads in every stored/reflected field and confirm they render inert; CSP report-only then enforce.

### SEC-20 — Cross-site request forgery (CSRF)

- **Detect:** Identify state-changing endpoints relying on cookie auth without CSRF tokens or SameSite protection.
- **Fix:** Use framework CSRF tokens or double-submit pattern, SameSite=Lax/Strict cookies, and Origin/Referer checks; never mutate on GET.
- **Verify:** Cross-origin form/fetch test without token is rejected; token round trip succeeds.
- **Also involves:** `session-jwt-oauth`

### SEC-21 — Insecure file uploads

- **Detect:** Review upload handlers for type/size checks, storage location, filename use, execution permissions and public access.
- **Fix:** Allowlist types by content not extension; cap size; generate server-side names; store outside web root or in private object storage; scan if risk warrants; serve with safe Content-Type and Content-Disposition.
- **Verify:** Upload test files (oversized, wrong type, double extension, traversal name) and confirm rejection; confirm uploaded files are not executable.
- **Also involves:** `injection-prevention`

### SEC-46 — Missing security headers

- **Detect:** Inspect response headers for HSTS, CSP, X-Content-Type-Options, frame-ancestors/X-Frame-Options, Referrer-Policy, Permissions-Policy.
- **Fix:** Set headers at the edge or framework; roll out CSP in report-only first; HSTS only after HTTPS is fully working.
- **Verify:** Header check against the deployed build (curl -I) and automated test in CI.
- **Also involves:** `cloud-config`

### SEC-47 — Insecure cookie settings

- **Detect:** Review Set-Cookie for HttpOnly, Secure, SameSite, Path/Domain scope and lifetime.
- **Fix:** Set HttpOnly, Secure, SameSite and minimal scope on session cookies; use __Host- prefix where suitable.
- **Verify:** Inspect Set-Cookie on login in a production-like environment and assert attributes.
- **Also involves:** `session-jwt-oauth`

### SEC-68 — Sensitive browser storage

- **Detect:** Check localStorage/sessionStorage/IndexedDB/cookies for tokens, PII or secrets.
- **Fix:** Prefer HttpOnly cookies for session credentials; avoid storing sensitive data client-side; clear on logout.
- **Verify:** Inspect browser storage after login/logout in a test run and assert no sensitive values.
- **Also involves:** `session-jwt-oauth`

### SEC-69 — Open redirects

- **Detect:** Find redirects driven by next/returnTo/url parameters, including OAuth flows.
- **Fix:** Allowlist destinations or accept only relative paths; validate after parsing; avoid reflecting raw URLs.
- **Verify:** Tests with absolute, protocol-relative, backslash and encoded URLs are rejected.
- **Also involves:** `session-jwt-oauth`

### PROD-22 — Security headers

- **Detect:** See SEC-46.
- **Fix:** See SEC-46.
- **Verify:** See SEC-46.
- **Also involves:** `production-readiness`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-14` Secrets in frontend JavaScript (owner: `secrets-detection`)
- `SEC-15` Client-only security (owner: `authentication-authorization`)
- `SEC-16` Missing or weak input validation (owner: `injection-prevention`)
- `SEC-22` Path traversal (owner: `injection-prevention`)
- `SEC-25` Weak session management (owner: `session-jwt-oauth`)
- `SEC-54` Misconfigured OAuth (owner: `session-jwt-oauth`)
- `SEC-65` Sensitive information leakage (owner: `crypto-data-protection`)
- `SEC-66` Invalid AI output (owner: `ai-agent-security`)
- `UX-03` Site search (owner: `website-interactions`)
- `UX-14` UTM tracking (owner: `consent-and-privacy-ui`)
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

- CSP and headers can break functionality; test before enforcing.
- Automated scanners miss DOM-based XSS in complex apps.
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

- `injection-prevention`
- `session-jwt-oauth`
- `cloud-config`
