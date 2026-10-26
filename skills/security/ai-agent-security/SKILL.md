---
name: ai-agent-security
description: 'Secure AI-powered features and coding agents: prompt injection, unpermissioned AI access, invalid AI output and excessive AI permissions. Use when an LLM reads untrusted content, calls tools, runs code, queries data or generates HTML/SQL/URLs/commands.'
license: MIT
metadata:
  category: security
  version: 0.1.0
---

# AI Agent Security

## Objective

Contain what an AI component can see and do, and treat its inputs and outputs as untrusted.

## When to Use

Use when: an LLM reads untrusted content, calls tools, runs code, queries data or generates HTML/SQL/URLs/commands.

Do not use for: Reviewing third-party skill files (skill-supply-chain-review).

## Scope

LLM calls, retrieval, tool/function calling, agent runtimes, MCP servers, generated-code execution.

## Workflow

1. Inspect the project (language, framework, dependencies, data stores, auth model, deployment target, test commands) before changing anything.
2. Select only the checks below that apply to the actual stack; record those skipped and why.
3. Enforce permissions in code and infrastructure, not only in prompts.
4. Require human approval for destructive or external actions.
5. Schema-validate structured outputs; encode for each sink.
6. Classify each result as **confirmed** (reproduced or directly evidenced by file and line, command output, or request/response) or **suspected** (pattern match or inference). Never present a suspicion as a confirmed finding.
7. Rank by severity, exploitability, exposure, confidence and business impact.
8. Explain the planned change, its effect, tests and possible breaking behaviour before any risky operation.
9. Make focused changes that preserve existing behaviour; avoid unrelated rewrites.
10. Verify using the commands under Verification and record exact outcomes.

## Detection Methods

- Map untrusted-input paths into context.
- Inventory tools, tokens and scopes.
- Adversarial test prompts against the integrated system.
- Check output sinks.

## Coverage

Items this skill owns. Each is individually traceable in `registry/coverage.json`.

### SEC-39 — Prompt injection

- **Detect:** Identify where untrusted text (web pages, emails, documents, tool output, user input) enters model context alongside instructions and tools.
- **Fix:** Separate trusted instructions from untrusted data; minimise tool permissions; require human confirmation for sensitive actions; validate outputs. Prompting alone does not eliminate the risk.
- **Verify:** Red-team test set of injection payloads; confirm sensitive actions are blocked by code-level controls, not just model compliance.

### SEC-40 — Unpermissioned AI access

- **Detect:** Check what data and tools an AI feature can reach and whether access respects the calling user's permissions.
- **Fix:** Run AI actions with the end user's authorization, not a service superuser; scope retrieval by user/tenant.
- **Verify:** Test that a user cannot obtain another user's data through the AI feature.
- **Also involves:** `api-access-control`

### SEC-66 — Invalid AI output

- **Detect:** Find places where model output is executed, rendered as HTML, used in SQL/URLs/commands, or trusted as structured data.
- **Fix:** Treat output as untrusted: schema-validate, encode for the sink, parameterise queries, allowlist URLs/commands, human confirmation for high impact.
- **Verify:** Tests feed malformed or hostile model output and confirm sinks reject or neutralise it.
- **Also involves:** `injection-prevention`, `web-input-security`

### SEC-67 — Excessive AI permissions

- **Detect:** Inventory tools, tokens, file/network/shell access given to agents or AI features.
- **Fix:** Grant least privilege, scoped short-lived credentials, sandbox execution, allowlisted commands, approval gates for destructive or external actions.
- **Verify:** Permission review table plus test showing denied actions are blocked by the platform, not only by prompt.
- **Also involves:** `security-audit`

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

- Prompt-injection defences are probabilistic; no instruction fully eliminates the risk.
- Model behaviour changes between versions; retest after upgrades.
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

- `injection-prevention`
- `web-input-security`
- `api-access-control`
- `skill-supply-chain-review`
