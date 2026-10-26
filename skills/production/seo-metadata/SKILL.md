---
name: seo-metadata
description: 'Implement and verify SEO and sharing metadata: titles, descriptions, social preview image, favicon, sitemap, robots.txt, canonical URLs and accurate last-updated dates. Use when launching or restructuring a public site.'
license: MIT
metadata:
  category: production
  version: 0.1.0
---

# Seo Metadata

## Objective

Make pages discoverable and shareable with accurate, unique metadata.

## When to Use

Use when: launching or restructuring a public site.

Do not use for: Content strategy or keyword research.

## Scope

HTML head, sitemap/robots files, structured data, icons.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Generate metadata from real page content.
4. Keep robots.txt consistent with intent; it is not access control.
5. Match structured data to visible content.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Crawl rendered pages for metadata.
- Validate sitemap URLs.
- Fetch robots.txt and icons.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### UX-18 — Accurate last-updated date

- **Detect:** Find hard-coded or build-time dates and decide what 'updated' means.
- **Fix:** Derive from real content change (git commit, CMS timestamp), machine-readable <time datetime>, align with structured data dateModified; never auto-bump without change.
- **Verify:** Change content and confirm date changes; unchanged content keeps date.
- **Also involves:** `website-interactions`

### PROD-06 — Meta titles and descriptions

- **Detect:** Crawl pages for missing, duplicate, over- or under-length titles/descriptions.
- **Fix:** Unique title and description per page generated from real content.
- **Verify:** Crawler script/lint finds no missing or duplicate values.

### PROD-07 — Social preview image

- **Detect:** Check og:image/twitter:image presence, size and absolute URL.
- **Fix:** Provide properly sized image with alt text and absolute URL; per-page where valuable.
- **Verify:** Inspect rendered meta tags; test with platform debuggers manually.

### PROD-08 — Favicon

- **Detect:** Check favicon.ico, SVG/PNG and touch icon links.
- **Fix:** Provide multiple sizes and web manifest where needed.
- **Verify:** Requests for icon URLs return 200 with correct type.

### PROD-09 — Sitemap and robots.txt

- **Detect:** Check presence, accuracy, absolute URLs, and that private/non-prod areas are not exposed.
- **Fix:** Generate sitemap from routes; robots.txt references sitemap; remember robots.txt is not access control.
- **Verify:** Fetch both files; validate URLs return 200; staging disallowed and authenticated.
- **Also involves:** `cloud-config`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `UX-14` UTM tracking (owner: `consent-and-privacy-ui`)
- `UX-19` Expandable FAQ (owner: `website-interactions`)
- `PROD-10` Image alt text (owner: `accessibility-responsive`)
- `PROD-19` Analytics configuration (owner: `consent-and-privacy-ui`)

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

- Search ranking cannot be guaranteed; platform preview rendering differs.
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

- `performance`
- `accessibility-responsive`
- `consent-and-privacy-ui`
