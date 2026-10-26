# Operating Model for Coding Agents

Phases an agent follows (also encoded in `security-audit`):

1. **Understand** - language, framework, dependencies, database, auth model, deployment target, test commands.
2. **Select skills** - by actual stack and risk; do not load or run everything.
3. **Audit** - collect evidence, map trust boundaries. Label results *confirmed* or *suspected*.
4. **Prioritise** - severity, exploitability, exposure, confidence, business impact.
5. **Plan** - changes, expected effects, tests, breaking risks, before risky operations.
6. **Remediate** - focused changes; keep behaviour; no unrelated rewrites.
7. **Verify** - run tests, linters, type checks, builds, scanners, and the per-item verification step; use controlled fixtures.
8. **Report** - findings, changes, commands run, observed outcomes, limitations, residual risk, unavailable checks.

## Human approval gates

Required before: destructive changes (including Git history rewrites), production deployment, credential rotation, any external side effect (emails, payments, third-party writes), material cloud permission changes, installing or running third-party skills or scripts.

## Reporting rules

- Never report a check as passed unless it ran and succeeded; use `unverified: <reason>`.
- Never include secret values in reports or logs; reference file and line.
- State residual risk. A checklist does not prove security.
