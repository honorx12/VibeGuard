---
name: website-interactions
description: 'Implement optional site interactions: dark mode, site search, back-to-top, loading and skeleton states, scroll progress, copy-to-clipboard, print stylesheet, expandable FAQ and floating contact action. Use only when the feature fits the product''s actual needs.'
license: MIT
metadata:
  category: frontend
  version: 0.1.0
---

# Website Interactions

## Objective

Add useful interactions accessibly, performantly and consistently with the existing design system.

## When to Use

Use when: Implement optional site interactions: dark mode, site search, back-to-top, loading and skeleton states, scroll progress, copy-to-clipboard, print stylesheet, expandable FAQ and floating contact action. Use only when the feature fits the product's actual needs.

Do not use for: Forms (forms-validation) and consent UI (consent-and-privacy-ui).

## Scope

Frontend components, CSS and small scripts.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Decide whether each feature is warranted; document skipped ones with reason.
4. Cover loading, empty, error and success states.
5. Respect prefers-reduced-motion and prefers-color-scheme.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Review existing components first.
- Cross-device and keyboard testing.
- Performance profile for scroll listeners.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### UX-01 — Dark mode toggle

- **Detect:** Check if design system already has theming tokens; decide if the product needs a toggle at all.
- **Fix:** Respect prefers-color-scheme by default; offer an explicit toggle persisted in a non-sensitive preference; use CSS variables; avoid flash of wrong theme.
- **Verify:** Contrast check in both themes; keyboard operable toggle with aria-pressed; no flash on reload; works with JS disabled via media query.
- **Also involves:** `accessibility-responsive`

### UX-03 — Site search

- **Detect:** Decide if content volume justifies search; pick static index (e.g. Pagefind-style) or backend search.
- **Fix:** Labelled search input, debounced queries, empty/error/loading states, escaped result rendering, rate-limited backend endpoint.
- **Verify:** Keyboard test; XSS payload in query renders inert; empty and error states visible; no-results message.
- **Also involves:** `rate-limits-abuse`, `web-input-security`

### UX-04 — Back-to-top button

- **Detect:** Only add for long pages; check it does not overlap sticky UI or floating contact action.
- **Fix:** Real button with accessible name; appears after scroll threshold; honour prefers-reduced-motion; move focus sensibly.
- **Verify:** Keyboard/focus test; reduced-motion test; no overlap on mobile viewports.
- **Also involves:** `accessibility-responsive`

### UX-06 — Loading animations and skeleton states

- **Detect:** Identify async views and their loading, empty, error and success states.
- **Fix:** Skeletons matching final layout to prevent layout shift; aria-busy/live region for status; timeouts with retry; respect reduced motion.
- **Verify:** Throttled-network test; CLS measurement; error state visible when request fails.
- **Also involves:** `performance`

### UX-08 — Scroll progress bar

- **Detect:** Only for long-form content; confirm it adds value.
- **Fix:** Decorative element (aria-hidden) or progress role if informative; use passive scroll listeners or CSS scroll timelines with fallback; reduced motion.
- **Verify:** No scroll jank in performance profile; hidden from assistive tech if decorative.
- **Also involves:** `performance`

### UX-09 — Copy-to-clipboard button

- **Detect:** Identify code blocks, codes, links worth copying.
- **Fix:** Native button with accessible name; navigator.clipboard with fallback and permission handling; announce success via live region; never auto-copy sensitive data.
- **Verify:** Works on HTTPS; failure state shown; screen-reader announcement; no secret content copied unintentionally.
- **Also involves:** `accessibility-responsive`

### UX-10 — Print stylesheet

- **Detect:** Check pages users plausibly print (articles, receipts, docs).
- **Fix:** @media print rules: hide nav/ads/interactive widgets, readable fonts, show link URLs where useful, avoid page breaks inside blocks.
- **Verify:** Print preview/PDF render check for key page types.

### UX-19 — Expandable FAQ

- **Detect:** Check content is genuinely Q&A; consider native details/summary.
- **Fix:** Prefer <details>/<summary> or button with aria-expanded/aria-controls; content crawlable; optional FAQ structured data only when it matches visible content.
- **Verify:** Keyboard and screen-reader test; content visible to crawlers; structured-data validator passes.
- **Also involves:** `accessibility-responsive`, `seo-metadata`

### UX-20 — Floating contact action

- **Detect:** Check overlap with cookie banner, back-to-top and mobile browser UI.
- **Fix:** Real link/button with accessible name; does not cover content or consent UI; respects safe-area insets; consider whether needed.
- **Verify:** Check at small viewports with banner open; keyboard reachable; does not block form fields.
- **Also involves:** `consent-and-privacy-ui`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `UX-05` Mobile navigation (owner: `accessibility-responsive`)
- `UX-07` Hover and focus states (owner: `accessibility-responsive`)
- `UX-11` Sticky headers (owner: `accessibility-responsive`)
- `UX-18` Accurate last-updated date (owner: `seo-metadata`)
- `PROD-20` Clear primary call to action (owner: `production-readiness`)

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

- Feature value depends on the product; do not add all features by default.
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
- `performance`
- `consent-and-privacy-ui`
- `seo-metadata`
