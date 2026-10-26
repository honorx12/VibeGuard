---
name: api-access-control
description: 'Detect and fix object-level and tenant-level access problems in APIs: cross-user access, IDOR/BOLA, mass assignment, unsafe API inputs, poor tenant isolation and unsecured endpoints. Use when reviewing REST/GraphQL/RPC endpoints or multi-tenant data access.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Api Access Control

## Objective

Guarantee that each API call can only reach objects and fields the caller is entitled to.

## When to Use

Use when: reviewing REST/GraphQL/RPC endpoints or multi-tenant data access.

Do not use for: Login and role design (authentication-authorization).

## Scope

REST, GraphQL, RPC and server actions; ORMs and queries; caches, search indexes and background jobs that touch tenant data.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Build a route table: route, auth required, object scope, input schema.
4. Fix by scoping queries to the authenticated principal and using explicit DTOs.
5. Add automated cross-account tests to the suite.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Enumerate routes and ID-bearing parameters.
- Two-account (and two-tenant) differential tests.
- Search for model binding of raw request bodies.
- Compare route inventory with intended public surface.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-06 — Cross-user access

- **Detect:** Trace each data read/write to see whether the owner or tenant is derived from the session or from client input.
- **Fix:** Derive user/tenant from the authenticated session; scope every query by owner; add DB-level row security where supported.
- **Verify:** Two-account test: user A cannot read, update or delete user B's records through any endpoint.
- **Also involves:** `authentication-authorization`

### SEC-33 — IDOR / BOLA

- **Detect:** For every endpoint taking an object ID, check whether ownership/permission is verified for that object.
- **Fix:** Authorize per object; use scoped queries; consider unguessable IDs as defence in depth, not as the control.
- **Verify:** Two-account automated test enumerating ID-bearing endpoints; cross-account access returns 403/404.
- **Also involves:** `authentication-authorization`

### SEC-34 — Unsafe APIs accepting untrusted input

- **Detect:** Review APIs for unvalidated bodies, overly broad filters, unbounded pagination/sorting, and dangerous parameters.
- **Fix:** Schema-validate; cap page size; allowlist sort/filter fields; return only needed fields.
- **Verify:** Fuzz-style tests with oversized, nested and unexpected inputs confirm bounded behaviour.
- **Also involves:** `injection-prevention`

### SEC-49 — Poor tenant isolation

- **Detect:** Check every query, cache key, file path, search index and background job for tenant scoping.
- **Fix:** Enforce tenant scope centrally (middleware, ORM scopes, row-level security); namespace caches and storage.
- **Verify:** Two-tenant test suite covering API, cache, search, exports and jobs.
- **Also involves:** `crypto-data-protection`

### SEC-51 — Mass assignment

- **Detect:** Find code binding request bodies directly to models (e.g. update(**request.json)) allowing fields like role, isAdmin, price.
- **Fix:** Use explicit allowlisted DTOs/serializers per operation; mark sensitive fields read-only.
- **Verify:** Send extra fields (role, tenant_id, is_admin) and confirm they are ignored or rejected.
- **Also involves:** `injection-prevention`

### SEC-70 — Unsecured endpoints

- **Detect:** Enumerate routes from code, OpenAPI, framework route dumps and logs; compare to documented intent; look for forgotten, legacy or test endpoints.
- **Fix:** Remove unused endpoints; apply default-deny authentication middleware; document intentionally public routes.
- **Verify:** Route inventory diff test: every route is either explicitly public or requires auth; CI fails on new unclassified routes.
- **Also involves:** `authentication-authorization`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-05` Missing authorization checks (owner: `authentication-authorization`)
- `SEC-07` Open database permissions (owner: `cloud-config`)
- `SEC-40` Unpermissioned AI access (owner: `ai-agent-security`)
- `SEC-41` Excessive database permissions (owner: `cloud-config`)

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

- Authorization intent must be confirmed by the application owner.
- GraphQL and nested resources need depth-specific testing.
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
- `injection-prevention`
- `cloud-config`
