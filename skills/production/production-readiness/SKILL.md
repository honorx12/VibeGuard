---
name: production-readiness
description: 'Run a pre-launch production-readiness review: HTTPS, custom 404, broken links, primary call to action, deployment checks and rollback planning, mapping every launch checklist item to a responsible skill. Use before releasing or handing over a website or web app.'
license: MIT
metadata:
  category: production
  version: 0.1.0
---

# Production Readiness

## Objective

Confirm the site is ready for real users with evidence for each checklist item.

## When to Use

Use when: Run a pre-launch production-readiness review: HTTPS, custom 404, broken links, primary call to action, deployment checks and rollback planning, mapping every launch checklist item to a responsible skill. Use before releasing or handing over a website or web app.

Do not use for: Deep security audit (security-audit).

## Scope

Built site, deployment settings and release process.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Walk the coverage map PROD-01..PROD-27 and mark each: pass, fail, not applicable, unverified.
4. Delegate to the specialist skill named per item.
5. Record evidence and owners for open items.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Crawl for broken links and status codes.
- Fetch headers and redirects.
- Run Lighthouse and accessibility checks when installed.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### PROD-04 — Enforce HTTPS

- **Detect:** Check redirects from HTTP, mixed content, certificate validity and renewal.
- **Fix:** Redirect HTTP to HTTPS at the edge; enable HSTS after validation; fix mixed content; automate renewal.
- **Verify:** curl -I http://… shows redirect; browser console shows no mixed content; certificate expiry monitored.
- **Also involves:** `crypto-data-protection`, `web-input-security`

### PROD-15 — Custom 404 page

- **Detect:** Request a non-existent URL and inspect status and body.
- **Fix:** Branded helpful 404 with navigation/search, real 404 status (not soft 404), no internal details.
- **Verify:** curl -i shows 404; page has no stack trace; links work.
- **Also involves:** `cloud-config`

### PROD-16 — Broken-link checks

- **Detect:** Crawl internal links and critical external links.
- **Fix:** Fix or redirect broken links; add 301s for moved pages; run link checker in CI with a polite crawl rate.
- **Verify:** Link-checker output shows zero broken internal links.

### PROD-20 — Clear primary call to action

- **Detect:** Identify the page's single main goal and current CTA prominence.
- **Fix:** One visually primary, descriptive CTA above the fold; consistent across pages; accessible and trackable.
- **Verify:** Stakeholder confirms goal; click path tested on mobile and desktop.
- **Also involves:** `website-interactions`

### PROD-21 — Deployment checks

- **Detect:** Review env config parity, migrations, health checks, feature flags and secrets injection.
- **Fix:** Pre-deploy checklist, health endpoint, staged rollout where feasible; human approval for production deploys.
- **Verify:** Checklist completed with evidence; smoke tests post-deploy.
- **Also involves:** `cloud-config`

### PROD-27 — Rollback planning

- **Detect:** Check ability to revert code, config and schema changes.
- **Fix:** Document rollback steps, keep previous artifact, use backwards-compatible migrations, define decision owner.
- **Verify:** Rollback rehearsed in staging; time to roll back measured.

### Supporting Role

Items owned elsewhere where this skill contributes:

- `PROD-03` Remove frontend secrets (owner: `secrets-detection`)
- `PROD-22` Security headers (owner: `web-input-security`)
- `PROD-23` Safe error handling (owner: `cloud-config`)
- `PROD-24` Dependency audits (owner: `dependency-supply-chain`)
- `PROD-25` Monitoring (owner: `logging-monitoring-backups`)
- `PROD-26` Backups and restore testing (owner: `logging-monitoring-backups`)

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

- A passing checklist is not a guarantee of quality or compliance.
- Items marked unverified must be reported as such.
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

- `security-audit`
- `performance`
- `seo-metadata`
- `accessibility-responsive`
- `consent-and-privacy-ui`
- `logging-monitoring-backups`
