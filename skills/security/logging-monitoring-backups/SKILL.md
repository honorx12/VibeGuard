---
name: logging-monitoring-backups
description: 'Establish audit logging, security monitoring and tested backups: missing audit logs, missing alerts, untested backups. Use when assessing operational readiness, incident detection or recovery capability.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Logging Monitoring Backups

## Objective

Ensure important events are recorded safely, alerts reach owners, and recovery has been demonstrated.

## When to Use

Use when: assessing operational readiness, incident detection or recovery capability.

Do not use for: Secret redaction in logs only (secrets-detection).

## Scope

Application and infrastructure logs, alert rules, backup jobs and restore procedures.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Define events, fields, retention and access.
4. Document RPO/RTO and run a restore drill in isolation (human approval).
5. Assign alert owners and runbooks.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Review log schema and sinks.
- Trigger test events and observe alerts.
- Check backup configuration and restore drill records.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-42 — Missing audit logs

- **Detect:** Check that logins, permission changes, admin actions, data exports and deletions produce tamper-resistant records.
- **Fix:** Add structured audit events (actor, action, target, time, outcome) without sensitive payloads; ship to append-only storage.
- **Verify:** Perform each audited action in test and confirm one event with required fields.

### SEC-43 — Missing security monitoring

- **Detect:** Check for alerting on auth failures, privilege changes, error spikes, unusual egress and rate-limit hits.
- **Fix:** Define alert rules and owners; route to an on-call channel; document runbooks.
- **Verify:** Trigger a test event and confirm an alert reaches its owner.

### SEC-44 — Missing or untested backups

- **Detect:** Check backup existence, frequency, retention, encryption, off-site copy and last successful restore test.
- **Fix:** Automate backups with retention and separate credentials; schedule restore drills; document RPO/RTO.
- **Verify:** Perform a restore into an isolated environment and record the result; a backup never restored is unverified.

### PROD-25 — Monitoring

- **Detect:** See SEC-43; add uptime, error-rate and latency checks.
- **Fix:** Uptime probe, error tracking, alert ownership.
- **Verify:** Synthetic failure triggers alert.
- **Also involves:** `production-readiness`

### PROD-26 — Backups and restore testing

- **Detect:** See SEC-44.
- **Fix:** Automated backups; scheduled restore drills.
- **Verify:** Restore drill result recorded.
- **Also involves:** `production-readiness`

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-11` Secrets in logs (owner: `secrets-detection`)
- `SEC-12` Verbose production errors (owner: `cloud-config`)
- `SEC-35` Exposed logs (owner: `cloud-config`)
- `SEC-65` Sensitive information leakage (owner: `crypto-data-protection`)

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

- Cannot verify off-platform backup health without access.
- A restore drill result is only valid for the date tested.
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
- `cloud-config`
- `crypto-data-protection`
