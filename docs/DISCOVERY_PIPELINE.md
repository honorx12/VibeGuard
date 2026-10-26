# Public Skill Discovery Pipeline

`scripts/discover_skills.py` builds a **catalogue**. It does not install, copy or execute anything.

## Sources and terms

Only the documented GitHub REST API is used (repository search, git tree listing, commit lookup) plus `raw.githubusercontent.com` for SKILL.md text when `--inspect` is set. No scraping, no authentication bypass. An optional `GITHUB_TOKEN` environment variable is sent only to `api.github.com`. Official specification and vendor documentation are read manually (see `agents/README.md`), not by the tool.

## Workflow

1. Search configured queries (`--query`, defaults in the script).
2. Record `source_url`, `repository_url`, author (repo owner), licence (SPDX from API, else `UNKNOWN`), retrieval date; `--resolve-revision` records the default-branch head SHA.
3. Normalise; reject malformed results (missing name/URL, non-https).
4. De-duplicate: same repository, or same name plus near-identical description.
5. Optional heuristic inspection of up to 5 `SKILL.md` files per repository for: pipe-to-shell, encoded execution, instruction override, concealment from the user, credential-file access, exfiltration patterns, destructive commands, safety bypass, privilege escalation, hidden Unicode, hidden HTML-comment instructions. Bundled `scripts/` directories are flagged, never run.
6. Write `registry/external-candidates.json` (schema validated) and, with `--report`, a review report.
7. **A human reads every file** before any adoption. Heuristics are indicators; an empty result does not mean safe, and a flagged result is not proof of malice.

## Licence handling

Permissive licences (MIT, Apache-2.0, BSD-2/3-Clause, ISC, CC0-1.0, Unlicense, CC-BY-4.0, 0BSD) are marked `permitted-by-license` and `pending-human-review`. Everything else, including unknown, is `link-only`: catalogue and link upstream, do not copy. Even permissive entries need attribution preserved if adopted.

## Review states

`pending-human-review` (default), `link-only`, `approved`, `rejected`. Re-running discovery preserves `approved`/`rejected` decisions. The tool never writes `approved`.

## Failure behaviour

Network errors, HTTP errors and malformed JSON are caught and reported as warnings. A rate-limit response (HTTP 403/429) stops further per-repository calls (circuit breaker) so the run finishes with partial data and says so. If every query fails, nothing is written and the exit code is 1.

## First run (2026-10-26)

See `docs/DISCOVERY_REPORT.md`. Searches succeeded; per-repository inspection and revision lookup hit the unauthenticated API limit for most entries, so those are flagged `inspection-failed` and have `revision: unresolved`. Re-run with `GITHUB_TOKEN` set to complete them.
