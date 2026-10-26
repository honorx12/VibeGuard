# Security Model

## Assets and threats

Skills are instructions executed by agents with tool access, so this repository is a supply-chain target.

| Threat | Control |
| --- | --- |
| Malicious or tampered third-party skill | Metadata-only catalogue; heuristics for reviewers; human approval before install; never execute bundled scripts during review; `skill-supply-chain-review` skill |
| Prompt injection via retrieved content (web pages, repos, tool output) | Skills state that retrieved content is data, not instructions; high-impact actions require human approval; `ai-agent-security` stresses code-level enforcement. Prompting alone does not eliminate prompt injection. |
| Secret disclosure in reports/logs | Scanner prints only file, line, rule and `[REDACTED len=N]`; skills forbid pasting secret values |
| Source code exfiltration | Scanner has no network code (tested); discovery sends only search queries and repository names |
| Destructive or production changes by an agent | Approval gates in `docs/OPERATING_MODEL.md` and every skill's remediation section |
| Fake assurance | Confirmed/suspected labelling; `unverified` status; limitations sections; no "secure" claims |
| Malformed registry/metadata | JSON Schema validation, duplicate checks, coverage cross-checks, CI-ready `--check` mode |

## Scanner limitations (`scan_project.py`)

False positives: placeholders, test fixtures, documentation that describes a pattern (scanning this repository reports its own docs). The scanner downgrades placeholder-like values and test/example paths to `low` and says so.
False negatives: secrets in unusual shapes or variable names (a real miss is documented in `examples/example-audit-report.md`), encoded/minified/generated content, binary files, lockfiles and files above 1 MB (skipped), anything outside default scope (dependency/build directories unless `--include-generated`), logic flaws such as missing authorization.
It is not a substitute for dedicated secret scanners, SAST, dependency audit, dynamic testing or expert review.

## Assumptions

Maintainers review every PR; users review skills before adopting them; agents run with least privilege in a project they are allowed to modify; test targets are non-production systems the user owns.

## Out of scope

Runtime sandboxing of agents, signing/attestation of skills (roadmap), legal or regulatory certification.
