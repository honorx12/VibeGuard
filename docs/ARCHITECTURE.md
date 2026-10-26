# Architecture

```text
skills/<category>/<name>/SKILL.md   instructions (the product)
registry/coverage.json              source of truth: item ID -> primary/secondary skill, detect/fix/verify
registry/skills-index.json          generated catalogue of first-party skills (schema-validated)
registry/external-candidates.json   metadata-only third-party catalogue (never installed)
registry/schema.json                JSON Schema (draft 2020-12) for both catalogues
docs/COVERAGE_MAP.md                generated from coverage.json
scripts/                            validate, scan, build, discover
tests/                              pytest suite + synthetic fixtures
agents/                             per-agent integration notes
```

## Design decisions

- **Portable format.** Skills use only the Agent Skills frontmatter fields (`name`, `description`, `license`, `metadata`) so they load wherever the spec is supported. Repository-specific conventions (required sections, line budget) are enforced by `validate_skills.py`, not by extra frontmatter.
- **Traceability.** Each coverage item has exactly one *primary* skill that documents it under a `### <ID> — <title>` heading. Supporting skills are listed but do not duplicate the detail. Validation fails if an item is missing, duplicated, or undocumented.
- **Progressive disclosure.** Skill bodies stay under 500 lines; only `name` and `description` need to be loaded for selection. Repository files are mentioned as plain paths (not links) so a skill copied alone still reads correctly; the orchestrator `security-audit` routes by stack so agents load few skills.
- **Generated vs authored.** `coverage.json` is authored; `COVERAGE_MAP.md` and `skills-index.json` are generated and checked with `build_registry.py --check`.
- **Offline by default.** Only `discover_skills.py` uses the network, with fixed hosts, https only, timeouts, size caps and mocked tests.

## Data flow for discovery

search (GitHub REST API) -> normalise -> dedupe -> optional heuristic inspection (read-only text) -> catalogue JSON + report -> **human review** -> manual adoption outside this tooling.
