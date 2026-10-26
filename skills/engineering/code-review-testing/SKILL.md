---
name: code-review-testing
description: 'Review code changes and test them: correctness, security-sensitive paths, AI-generated code scrutiny, regression tests and verification discipline. Use when reviewing a diff or PR or when remediation needs tests.'
license: MIT
metadata:
  category: engineering
  version: 0.1.0
---

# Code Review Testing

## Objective

Ensure changes are understood, reviewed, tested and honestly reported.

## When to Use

Use when: reviewing a diff or PR or when remediation needs tests.

Do not use for: Whole-repo security audit (security-audit).

## Scope

Diffs, tests, linters, type checkers and CI results.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Identify intent, then risk areas (auth, input, money, data).
4. Run commands and record exact results.
5. Report failed or unavailable checks explicitly.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Read the diff and connected code.
- Run the project's test, lint and type commands.
- Add targeted regression tests.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

This skill owns no individual items; it coordinates the specialist skills.

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-50` Unreviewed code (owner: `security-audit`)

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

- Cannot replace human review for high-impact changes.
- Passing tests only show tested behaviour.
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
- `skill-supply-chain-review`
