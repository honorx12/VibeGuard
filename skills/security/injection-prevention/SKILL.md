---
name: injection-prevention
description: 'Prevent injection and unsafe input handling: missing validation, SQL and NoSQL injection, command injection, insecure deserialization and path traversal. Use when code builds queries, shell commands, file paths or deserializes data.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# Injection Prevention

## Objective

Make every interpreter and file-system sink receive parameterised or allowlisted data only.

## When to Use

Use when: code builds queries, shell commands, file paths or deserializes data.

Do not use for: Browser output encoding (web-input-security).

## Scope

Data stores, shells, file APIs, deserializers, templating of non-HTML interpreters.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. List sinks, then fix highest exposure first.
4. Prefer parameterisation and safe APIs over escaping.
5. Add regression tests with payloads.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Trace tainted input to sinks.
- Static analysis rules (e.g. semgrep or language linters) when installed.
- Payload regression tests.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-16 — Missing or weak input validation

- **Detect:** Map all inputs (body, query, headers, files, webhooks, env) and check for schema validation on type, length, range and format.
- **Fix:** Validate at the boundary with a schema library; allowlist formats; reject unknown fields; validate again on the server.
- **Verify:** Negative tests with malformed, oversized, wrong-type and boundary values return 4xx and never reach business logic.
- **Also involves:** `web-input-security`

### SEC-17 — SQL injection

- **Detect:** Find string-built SQL (concatenation, f-strings, template literals) and ORM raw-query escapes; use SAST rules.
- **Fix:** Use parameterised queries/prepared statements; allowlist dynamic identifiers; least-privilege DB role.
- **Verify:** Regression test with injection payloads against each query path; static scan shows no string-built SQL.
- **Also involves:** `cloud-config`

### SEC-18 — NoSQL injection

- **Detect:** Look for query objects built directly from request JSON (e.g. operators like $ne, $gt, $where) and unsanitised filters.
- **Fix:** Validate types so operators cannot be injected; strip/deny $-prefixed keys; avoid server-side JS evaluation.
- **Verify:** Send operator payloads in login and filter endpoints and confirm rejection.

### SEC-22 — Path traversal

- **Detect:** Find file reads/writes/serves built from user input (path join, send_file, archive extraction).
- **Fix:** Resolve to canonical path and verify it stays inside an allowed base directory; use ID-to-path lookup rather than raw names; safe archive extraction.
- **Verify:** Tests with ../, encoded and absolute path payloads return 4xx and never touch files outside the base.
- **Also involves:** `web-input-security`

### SEC-52 — Command injection

- **Detect:** Find shell execution with user input (exec, system, subprocess with shell=True, backticks).
- **Fix:** Avoid shells; use argument-array APIs or native libraries; allowlist values.
- **Verify:** Payload tests with ; | $() and newlines produce no command execution; static scan has no shell=True on tainted input.

### SEC-53 — Insecure deserialization

- **Detect:** Find pickle, yaml.load, Java ObjectInputStream, PHP unserialize, unsafe JSON revivers on untrusted data.
- **Fix:** Use safe data formats (JSON with schema); safe loaders; never deserialize untrusted native objects; sign data if state must round trip.
- **Verify:** Static scan shows no unsafe loaders on untrusted input; malicious-object test is rejected.

### Supporting Role

Items owned elsewhere where this skill contributes:

- `SEC-21` Insecure file uploads (owner: `web-input-security`)
- `SEC-34` Unsafe APIs accepting untrusted input (owner: `api-access-control`)
- `SEC-51` Mass assignment (owner: `api-access-control`)
- `SEC-66` Invalid AI output (owner: `ai-agent-security`)
- `UX-16` Form error states (owner: `forms-validation`)
- `PROD-17` Form validation (owner: `forms-validation`)

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

- Taint tracing by reading code is incomplete for dynamic code paths.
- Do not run live payloads against systems you do not own.
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

- `web-input-security`
- `api-access-control`
