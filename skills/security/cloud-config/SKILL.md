---
name: cloud-config
description: 'Audit deployment and cloud configuration: open DB permissions, cloud misconfiguration, admin/debug exposure, verbose errors, exposed environments, logs, source maps, dashboards and DB roles. Use when reviewing IaC, hosting settings, Docker/Kubernetes config or release builds.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Cloud Config

## Objective

Verify infrastructure and runtime configuration follows least privilege and exposes nothing unintended.

## When to Use

Use when: reviewing IaC, hosting settings, Docker/Kubernetes config or release builds.

Do not use for: Application-level authorization logic (api-access-control).

## Scope

Terraform/CloudFormation/Pulumi, Dockerfiles, Kubernetes manifests, hosting settings, DB grants, DNS and public endpoints of test deployments.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Never apply infrastructure changes automatically; produce a plan for approval.
4. Compare IaC to live state when access is granted.
5. Separate prod/non-prod secrets and data.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- IaC scanners where installed (checkov, trivy).
- Read-only cloud inspection with human-approved credentials.
- External reachability checks against hosts you own.
- Build output inspection for maps and debug assets.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-07 — Open database permissions

- **Detect:** Inspect DB roles, grants, row-level-security status, public buckets/collections, and network rules (e.g. 0.0.0.0/0).
- **Fix:** Create least-privilege roles per service; enable row-level security or equivalent; close public network access.
- **Verify:** Connect with the application role and confirm only intended tables/operations succeed; external connection attempts fail.
- **Also involves:** `api-access-control`

### SEC-08 — Cloud service misconfiguration

- **Detect:** Review IaC and console exports for public storage, wide IAM policies, disabled encryption/logging, open security groups. Use IaC scanners where available (e.g. checkov, tfsec/trivy).
- **Fix:** Apply least-privilege IAM, private-by-default storage, encryption at rest, logging enabled; manage via reviewed IaC.
- **Verify:** Re-run IaC scanner and attach output; confirm with a read-only cloud inspection (human-approved) that live state matches IaC.

### SEC-10 — Exposed production debug tools

- **Detect:** Look for DEBUG=true, debug toolbars, profilers, /actuator, /_debug, GraphQL introspection or playgrounds, Swagger UI enabled in production.
- **Fix:** Gate debug features on environment; disable or authenticate diagnostic endpoints; separate prod and dev config.
- **Verify:** Request known debug paths on the production-like build and confirm 401/403/404; confirm DEBUG is false in effective config.

### SEC-12 — Verbose production errors

- **Detect:** Trigger errors in a production-mode build and check for stack traces, SQL, file paths, framework banners.
- **Fix:** Return generic error bodies with a correlation ID; log detail server-side only; set production error handlers.
- **Verify:** Force 400/404/500 conditions and assert response bodies contain no stack trace, path or query text.
- **Also involves:** `logging-monitoring-backups`

### SEC-29 — Exposed development and staging environments

- **Detect:** Enumerate dev/staging hosts and URLs referenced in repo/DNS; check authentication and indexing.
- **Fix:** Put non-prod behind SSO/VPN/IP allowlist; use separate data and secrets; add noindex and auth.
- **Verify:** Unauthenticated request to each non-prod host is denied; no production data present.

### SEC-35 — Exposed logs

- **Detect:** Check for publicly reachable log files, log dashboards, storage buckets and verbose log endpoints.
- **Fix:** Store logs in access-controlled systems; remove log files from web roots; authenticate dashboards.
- **Verify:** Unauthenticated access attempts to log paths/dashboards are denied.
- **Also involves:** `logging-monitoring-backups`

### SEC-36 — Exposed source maps

- **Detect:** Check build output and deployed host for *.map files and sourceMappingURL comments.
- **Fix:** Disable public source maps in production or upload them privately to error-tracking only.
- **Verify:** Request known .map URLs on the production build: expect 404; scan dist for sourceMappingURL.
- **Also involves:** `secrets-detection`

### SEC-41 — Excessive database permissions

- **Detect:** Review the DB account used by the app, migrations and AI tools for DDL, superuser or cross-schema rights.
- **Fix:** Separate migration and runtime roles; grant minimum table/column privileges; read-only roles for analytics and AI.
- **Verify:** Attempt a forbidden statement (e.g. DROP) with the runtime role in a test DB: it must fail.
- **Also involves:** `api-access-control`

### SEC-45 — Exposed internal dashboards

- **Detect:** Find admin/monitoring tools (Grafana, Kibana, queues, DB UIs, feature-flag consoles) reachable publicly.
- **Fix:** Place behind SSO/VPN/allowlist; disable anonymous access; change default credentials.
- **Verify:** External unauthenticated request to each dashboard returns login/deny.
- **Also involves:** `authentication-authorization`

### PROD-23 — Safe error handling

- **Detect:** See SEC-12; check user-facing error pages.
- **Fix:** Generic messages, correlation IDs, no internals.
- **Verify:** Forced error tests.
- **Also involves:** `production-readiness`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-01` Exposed database credentials (owner: `secrets-detection`)
- `SEC-02` Public .env files (owner: `secrets-detection`)
- `SEC-09` Unprotected admin routes (owner: `authentication-authorization`)
- `SEC-17` SQL injection (owner: `injection-prevention`)
- `SEC-23` Server-side request forgery (SSRF) (owner: `ssrf-cors-webhooks`)
- `SEC-46` Missing security headers (owner: `web-input-security`)
- `SEC-48` Unencrypted sensitive data (owner: `crypto-data-protection`)
- `PROD-09` Sitemap and robots.txt (owner: `seo-metadata`)
- `PROD-15` Custom 404 page (owner: `production-readiness`)
- `PROD-21` Deployment checks (owner: `production-readiness`)

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

- Live cloud state cannot be assessed from code alone.
- Scanner rule sets differ and miss provider-specific details.
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
- `logging-monitoring-backups`
- `crypto-data-protection`
- `web-input-security`
