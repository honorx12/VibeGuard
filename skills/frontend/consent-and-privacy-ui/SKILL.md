---
name: consent-and-privacy-ui
description: 'Handle privacy and consent interfaces: cookie banner and preferences, UTM tracking, analytics configuration, privacy policy and terms drafting based on actual behaviour. Use when a site uses cookies, trackers, analytics or collects personal data.'
license: MIT
metadata:
  category: frontend
  version: 0.1.0
---

# Consent And Privacy Ui

## Objective

Make tracking and data handling transparent, consent-gated where required, and documentation accurate.

## When to Use

Use when: a site uses cookies, trackers, analytics or collects personal data.

Do not use for: Providing legal advice or certifying compliance.

## Scope

Cookie/tracker inventory, consent UI, analytics scripts, policy and terms documents.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Inventory first; add banner only if non-essential tracking exists.
4. Gate scripts on consent; offer equal reject option.
5. Mark policy gaps for owner and counsel.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Network inspection before and after consent.
- Cookie and storage inventory.
- Compare policy text with actual data flows.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### UX-02 — Cookie banner and preferences

- **Detect:** Inventory cookies/trackers and applicable regimes (e.g. GDPR/ePrivacy, UK PECR, CCPA/CPRA); banner only if non-essential tracking exists.
- **Fix:** Block non-essential scripts until consent; equal-prominence accept/reject; granular preferences; persistent re-open link; store consent record.
- **Verify:** Network test: no analytics/ad requests before consent; reject path works; preferences reachable from footer. Legal sufficiency needs counsel.
- **Also involves:** `accessibility-responsive`

### UX-14 — UTM tracking

- **Detect:** Decide whether campaign tracking is needed and whether consent is required.
- **Fix:** Parse utm_* parameters only after consent where required; allowlist keys, length-limit and encode values; never store personal data in UTM values; strip from canonical URLs.
- **Verify:** Test: payload in utm_source renders inert and is not stored raw; no tracking before consent.
- **Also involves:** `seo-metadata`, `web-input-security`

### PROD-01 — Privacy policy

- **Detect:** Inventory personal data collected, processors, retention, transfers, rights and contact details from the actual code and vendors.
- **Fix:** Draft a policy matching real behaviour; flag fields needing business input; link from footer and forms. Template text is not legal compliance.
- **Verify:** Compare policy against data inventory; request legal review. Never claim compliance.

### PROD-02 — Terms and conditions

- **Detect:** Identify services, payments, user content, liability and jurisdiction facts.
- **Fix:** Draft from actual product facts; mark gaps for owner and counsel; link at signup/checkout.
- **Verify:** Owner and legal review recorded; links reachable.

### PROD-05 — Cookie consent where applicable

- **Detect:** Determine if non-essential cookies/trackers exist and which regimes apply.
- **Fix:** Implement consent gating only where needed; see UX-02.
- **Verify:** No non-essential requests before consent.

### PROD-19 — Analytics configuration

- **Detect:** Inventory analytics tags, data collected, consent dependency, IP handling and retention.
- **Fix:** Configure minimal events, consent gating where required, anonymisation settings, no PII in event payloads.
- **Verify:** Network inspection before/after consent; test property receives expected events only after consent.
- **Also involves:** `seo-metadata`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `UX-20` Floating contact action (owner: `website-interactions`)

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

- Legal requirements vary by jurisdiction; generated documents are drafts and need legal review.
- Never state that the site is compliant.
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
- `seo-metadata`
- `crypto-data-protection`
