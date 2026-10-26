# Contributing

1. Read `docs/SKILL_AUTHORING_GUIDE.md`.
2. Install dev dependencies: `pip install -r requirements-dev.txt`.
3. Edit or add a skill under `skills/<category>/<name>/SKILL.md`. The directory name must equal the `name` field.
4. If you add, rename or re-map a coverage item, edit `registry/coverage.json`, then run `python scripts/build_registry.py`.
5. Before opening a PR run:
   ```bash
   python scripts/validate_skills.py
   python scripts/build_registry.py --check
   python -m pytest
   ruff check .
   ```
6. In the PR, state which commands you ran and their real results. Do not claim checks that did not run.

## Rules

- One focused purpose per skill; link to other skills instead of duplicating them.
- Every remediation needs a verification step. Never write guidance that claims a system is secure after a checklist passes.
- No real secrets, even in examples or fixtures. Use obviously fake values; generate token-shaped strings at test time.
- Do not copy third-party skill text unless the licence clearly permits it; record attribution. Prefer a catalogue entry that links upstream.
- New or changed network behaviour needs mocked tests.
- Security issues in this repository: see `SECURITY.md`.

## Versioning

Semantic versioning. Skill `metadata.version` tracks the library version; bump it in changed skills and note changes in `CHANGELOG.md`.
