# Synthetic security test cases

All values here are invented. None are real credentials. They exist only to exercise
`scripts/scan_project.py` and the skill guidance.

- `vulnerable-app/` – intentionally unsafe patterns the scanner should report as *candidates*.
- `clean-app/` – a small project the scanner should not flag.
- `ignored-dirs/` – matches inside dependency/build directories that must be skipped by default.

Token-format secrets (AWS-style, GitHub-style) are generated at test time inside temporary
directories so that this repository does not itself contain secret-shaped strings.
