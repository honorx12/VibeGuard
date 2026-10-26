---
name: accessibility-responsive
description: 'Implement and verify accessibility and responsive behaviour: focus and hover states, skip links, mobile navigation, sticky headers, image alt text, colour contrast and mobile layouts. Use when building or reviewing UI components and pages.'
license: MIT
metadata:
  category: frontend
  version: 0.1.0
---

# Accessibility Responsive

## Objective

Make interfaces usable by keyboard, assistive technology and small screens, meeting WCAG 2.2 AA as a target.

## When to Use

Use when: building or reviewing UI components and pages.

Do not use for: Visual branding decisions; legal accessibility certification.

## Scope

Markup, CSS, component libraries and rendered pages.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Follow existing design-system conventions.
4. Fix semantics first, ARIA only when native elements are insufficient.
5. Re-test after each change.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Keyboard-only walkthrough.
- Automated checks (axe-core, Lighthouse) when installed.
- Viewport sweep from 320px.
- Contrast calculation of design tokens.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### UX-05 — Mobile navigation

- **Detect:** Check breakpoints and existing nav component.
- **Fix:** Button with aria-expanded/aria-controls; focus management and Escape to close; touch targets at least 24px (aim 44px); works without hover.
- **Verify:** Test at 320px width and with keyboard and screen-reader smoke test; focus returns to trigger on close.
- **Also involves:** `website-interactions`

### UX-07 — Hover and focus states

- **Detect:** Check all interactive elements for visible focus and non-hover alternatives.
- **Fix:** Visible :focus-visible styles with sufficient contrast; hover never the only affordance; consistent states for disabled/active.
- **Verify:** Tab through each page; automated axe-style check; focus indicator contrast verified.
- **Also involves:** `website-interactions`

### UX-11 — Sticky headers

- **Detect:** Check header height versus viewport and anchor links.
- **Fix:** Use position: sticky with scroll-padding-top so anchors and focus are not hidden; keep compact on mobile; ensure focus not obscured (WCAG 2.2).
- **Verify:** Keyboard focus never hidden under header; 400% zoom check; anchor jump check.
- **Also involves:** `website-interactions`

### UX-12 — Skip-to-content link

- **Detect:** Check first focusable element on every layout.
- **Fix:** First focusable link targeting main landmark id; visible on focus; main has tabindex=-1 if needed.
- **Verify:** Tab once from page load: link appears and moves focus to main content.

### PROD-10 — Image alt text

- **Detect:** Find images without alt or with filename-like alt.
- **Fix:** Meaningful alt for informative images, empty alt for decorative, text alternatives for complex images.
- **Verify:** Lint/axe finds no missing alt; manual spot check of quality.
- **Also involves:** `seo-metadata`

### PROD-13 — Color contrast

- **Detect:** Check text and UI component contrast against WCAG 2.2 AA (4.5:1 text, 3:1 large text/UI).
- **Fix:** Adjust tokens; do not rely on colour alone.
- **Verify:** Automated checker plus manual review of states and both themes.

### PROD-14 — Mobile responsiveness

- **Detect:** Test viewports from 320px; check horizontal scroll, tap targets, zoom.
- **Fix:** Responsive layout with relative units; viewport meta; avoid disabling zoom.
- **Verify:** Viewport sweep (320, 375, 768, 1280) with screenshots or automated checks.

### Supporting Role

Items owned elsewhere where this skill contributes:

- `UX-01` Dark mode toggle (owner: `website-interactions`)
- `UX-02` Cookie banner and preferences (owner: `consent-and-privacy-ui`)
- `UX-04` Back-to-top button (owner: `website-interactions`)
- `UX-09` Copy-to-clipboard button (owner: `website-interactions`)
- `UX-15` Form success states (owner: `forms-validation`)
- `UX-17` Confirmation dialogs (owner: `forms-validation`)
- `UX-19` Expandable FAQ (owner: `website-interactions`)

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

- Automated tools catch only a portion of accessibility issues; manual and assistive-technology testing is required.
- Does not constitute a conformance claim.
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

- `website-interactions`
- `forms-validation`
- `performance`
