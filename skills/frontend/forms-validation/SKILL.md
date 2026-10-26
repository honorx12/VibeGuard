---
name: forms-validation
description: 'Build and review forms: password visibility toggle, success and error states, confirmation dialogs, validation, and spam protection. Use when creating or auditing any user input form.'
license: MIT
metadata:
  category: frontend
  version: 0.1.0
---

# Forms Validation

## Objective

Provide accessible forms with server-authoritative validation and clear states.

## When to Use

Use when: creating or auditing any user input form.

Do not use for: Server-side injection analysis (injection-prevention).

## Scope

Form components, validation logic, submit handlers, spam controls, dialogs.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Validate on the server; mirror on the client for UX.
4. Associate errors with fields; move focus to errors.
5. Prevent double-submit; add layered spam protection.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Submit valid, invalid, empty and hostile input.
- Screen-reader announcement check.
- Review server validation parity.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### UX-13 — Password visibility toggle

- **Detect:** Check auth forms and password-manager compatibility.
- **Fix:** Toggle button with accessible name and state; keep input type switching safe; correct autocomplete attributes; do not log or persist value.
- **Verify:** Keyboard and screen-reader test; password manager still fills; value not exposed in DOM attributes or analytics.
- **Also involves:** `authentication-authorization`

### UX-15 — Form success states

- **Detect:** Identify all submit paths and what the user needs to know afterwards.
- **Fix:** Clear confirmation message in a live region, preserved context, next step, prevention of duplicate submits, no sensitive echo.
- **Verify:** Submit test confirms message announced to screen readers and double-click does not duplicate.
- **Also involves:** `accessibility-responsive`

### UX-16 — Form error states

- **Detect:** Review validation messaging and server error mapping.
- **Fix:** Inline errors associated via aria-describedby, error summary with focus, specific actionable text, server-side validation as authority, no sensitive details in messages.
- **Verify:** Invalid, empty and server-error submissions tested; errors announced; focus moves to summary or first error.
- **Also involves:** `injection-prevention`

### UX-17 — Confirmation dialogs

- **Detect:** Identify destructive or irreversible actions.
- **Fix:** Use accessible modal (focus trap, Escape, restores focus, role=dialog/alertdialog) with explicit action labels; consider undo instead of confirm; server enforces authorization regardless.
- **Verify:** Keyboard test; cancel is safe default; destructive action still requires server-side authorization.
- **Also involves:** `accessibility-responsive`

### PROD-17 — Form validation

- **Detect:** Review client and server validation parity.
- **Fix:** Server-side validation authoritative; client-side for UX; accessible messages; see SEC-16.
- **Verify:** Invalid inputs rejected on server regardless of client.
- **Also involves:** `injection-prevention`

### PROD-18 — Spam protection

- **Detect:** Check public forms for abuse controls.
- **Fix:** Layered: rate limiting, honeypot, server verification of challenge tokens (privacy-aware CAPTCHA if justified), email verification where appropriate.
- **Verify:** Automated submissions bounded; verification done server-side; legitimate users not blocked in test.
- **Also involves:** `rate-limits-abuse`

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

- CAPTCHA choices involve privacy and accessibility tradeoffs requiring owner decision.
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
- `rate-limits-abuse`
- `accessibility-responsive`
- `authentication-authorization`
