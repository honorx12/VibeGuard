---
name: performance
description: 'Measure and improve page-load performance: Core Web Vitals, bundle size, image compression, caching and font loading. Use when pages are slow, before launch, or when adding heavy assets or scripts.'
license: MIT
metadata:
  category: production
  version: 0.1.0
---

# Performance

## Objective

Establish budgets, measure before and after, and apply targeted optimisations.

## When to Use

Use when: pages are slow, before launch, or when adding heavy assets or scripts.

Do not use for: Backend scaling and database tuning.

## Scope

Frontend assets, build output, caching headers, CDN settings.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Record baseline numbers.
4. Optimise biggest wins first (images, blocking scripts, JS size).
5. Re-measure and compare.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Lighthouse or equivalent lab run.
- Bundle analyzer output.
- Field data (CrUX/RUM) when available.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### PROD-11 — Image compression

- **Detect:** List large images and formats in build output.
- **Fix:** Modern formats (WebP/AVIF) with fallbacks, responsive srcset, lazy loading below fold, explicit width/height.
- **Verify:** Build report sizes compared to budget; Lighthouse image audits.

### PROD-12 — Page-load performance checks

- **Detect:** Measure Core Web Vitals (LCP, INP, CLS) and bundle size lab and field where available.
- **Fix:** Set budgets; reduce blocking scripts; code split; cache headers; fonts strategy.
- **Verify:** Run Lighthouse or equivalent before/after and record numbers; lab results do not equal field results.

### Supporting Role

Items owned elsewhere where this skill contributes:

- `UX-06` Loading animations and skeleton states (owner: `website-interactions`)
- `UX-08` Scroll progress bar (owner: `website-interactions`)

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

- Lab numbers vary between runs and differ from field data; report both when available.
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

- `accessibility-responsive`
- `website-interactions`
- `seo-metadata`
