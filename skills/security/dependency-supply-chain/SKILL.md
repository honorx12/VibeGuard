---
name: dependency-supply-chain
description: 'Assess dependency and build supply-chain risk: vulnerable and malicious packages, insecure CI/CD, untrusted build actions and unpinned dependencies. Use when adding packages, editing workflows, building images or auditing lockfiles.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Dependency Supply Chain

## Objective

Reduce exposure from third-party code and build systems with pinning, review and least-privilege pipelines.

## When to Use

Use when: adding packages, editing workflows, building images or auditing lockfiles.

Do not use for: Reviewing AI skill files (skill-supply-chain-review).

## Scope

Manifests, lockfiles, Dockerfiles, CI workflow files and registries.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Check lockfile presence and integrity.
4. Pin third-party actions to full commit SHA and images to digests.
5. Limit workflow token permissions; keep secrets from untrusted PRs.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Ecosystem audit tools (npm audit, pip-audit, osv-scanner, cargo audit).
- Workflow linters (actionlint, zizmor) when installed.
- Manual review of new dependencies and install scripts.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-37 — Vulnerable dependencies

- **Detect:** Run ecosystem audit tools (npm audit, pip-audit, osv-scanner, cargo audit, etc.) against lockfiles; review transitive depth.
- **Fix:** Upgrade or replace vulnerable packages; document accepted risk with expiry; enable automated update PRs for review.
- **Verify:** Re-run audit after changes and attach output; run the test suite on upgraded versions.

### SEC-38 — Malicious packages

- **Detect:** Review new/changed dependencies for typosquatting, install scripts, unknown maintainers, recent ownership changes.
- **Fix:** Remove suspicious packages; require review for new dependencies; use lockfiles with integrity hashes; consider install-script restrictions.
- **Verify:** Dependency diff reviewed and approved by a human; lockfile integrity verified in CI.
- **Also involves:** `skill-supply-chain-review`

### SEC-60 — Insecure CI/CD

- **Detect:** Review pipeline permissions, secret exposure to forks/PRs, self-hosted runners, script injection through untrusted inputs, deploy credentials.
- **Fix:** Least-privilege tokens; no secrets to untrusted PRs; avoid interpolating untrusted data into shell; protect deploy branches and environments.
- **Verify:** Review workflow files against a checklist/linter (e.g. actionlint, zizmor) and attach output.
- **Also involves:** `security-audit`

### SEC-61 — Untrusted build actions

- **Detect:** Inventory third-party actions, orbs, plugins and base images; check source, maintainers and reference style.
- **Fix:** Prefer vetted publishers; pin to full commit SHA or digest; review updates; minimise third-party steps.
- **Verify:** Lint shows no mutable-tag references for third-party actions; digest pins present for base images.

### SEC-62 — Unpinned build dependencies

- **Detect:** Check for floating versions, missing lockfiles, curl|sh installers, latest tags.
- **Fix:** Commit lockfiles; pin versions and hashes; pin image digests; use reproducible build settings.
- **Verify:** Clean build in CI from lockfile succeeds; diff of lockfile reviewed on updates.

### PROD-24 — Dependency audits

- **Detect:** See SEC-37.
- **Fix:** See SEC-37.
- **Verify:** Audit output attached.
- **Also involves:** `production-readiness`

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

- Audit databases lag disclosure; zero findings does not mean zero vulnerabilities.
- Malicious-package detection by heuristics is incomplete.
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
- `secrets-detection`
