---
name: payment-business-logic
description: 'Protect payment and business-logic integrity: frontend-only payment verification, workflow abuse and race conditions. Use when handling checkout, subscriptions, credits, coupons, inventory, refunds or any multi-step stateful workflow.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Payment Business Logic

## Objective

Make money and entitlement decisions server-side, atomically and idempotently.

## When to Use

Use when: handling checkout, subscriptions, credits, coupons, inventory, refunds or any multi-step stateful workflow.

Do not use for: Generic webhook signature work (ssrf-cors-webhooks), though they work together here.

## Scope

Checkout and subscription flows, pricing, coupons, credits, inventory, state machines, concurrency.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Never trust client price or status.
4. Use transactions, constraints, idempotency keys.
5. Test with provider sandbox, never live payments.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Workflow modelling: states, transitions, invariants.
- Concurrent-request tests in test mode.
- Review provider verification code.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-32 — Frontend-only payment verification

- **Detect:** Check whether order success, price, entitlement or plan is decided from client redirect/query state.
- **Fix:** Confirm payment server-side via provider API or verified webhook; compute prices on the server; grant entitlements only after verified events.
- **Verify:** Test with provider test mode: forged success redirect without payment grants nothing.
- **Also involves:** `ssrf-cors-webhooks`

### SEC-57 — Business logic abuse

- **Detect:** Model workflows (coupons, credits, refunds, referrals, quotas, negative numbers, step skipping) and look for abuse paths.
- **Fix:** Enforce state machines and invariants on the server; limit and monitor high-value actions.
- **Verify:** Abuse-case tests for each workflow invariant (negative amounts, repeated coupon, skipped step).
- **Also involves:** `rate-limits-abuse`

### SEC-58 — Race conditions

- **Detect:** Look for check-then-act sequences on balances, inventory, coupons, uniqueness without locks/constraints.
- **Fix:** Use transactions, row locks, unique constraints, atomic updates and idempotency keys.
- **Verify:** Concurrent request test (parallel calls) confirms single success.

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-15` Client-only security (owner: `authentication-authorization`)
- `SEC-31` Unsigned webhooks (owner: `ssrf-cors-webhooks`)
- `SEC-59` Webhook replay (owner: `ssrf-cors-webhooks`)

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

- Domain rules must come from the business owner.
- Race conditions are hard to reproduce deterministically.
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

- `ssrf-cors-webhooks`
- `rate-limits-abuse`
- `api-access-control`
