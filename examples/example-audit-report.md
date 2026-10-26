# Example Audit Report: `examples/sample-web-app`

> Illustrative report in the format the skills require. Target is a synthetic, intentionally vulnerable demo.
> **No fixes were applied and no application code was executed**, so every verification below is `unverified`.

## Commands executed

```bash
python scripts/scan_project.py examples/sample-web-app      # exit 0, 8 candidates, 5 files scanned
```

Not run: dependency audit (no lockfile, no installed deps), SAST, dynamic testing, secret scanner with history
(demo is not a git repository). These are **unavailable checks**, not passes.

## Scanner candidates and how each was classified

| Candidate (scanner output) | Classification | Reason |
| --- | --- | --- |
| `env-file-present` `.env` (medium) | **Confirmed** file exists; exposure **suspected** | No `.gitignore`; whether it is web-served depends on deployment (unknown). |
| `db-url-with-password` `.env:1` (medium) | **Confirmed** credential-shaped literal (demo value) | Read directly. In a real project: rotate, then move to a secret manager (SEC-01). |
| `debug-enabled` `.env:2`, `app.py:26` (low) | **Confirmed** in code | `app.run(debug=True)` bound to `0.0.0.0` (SEC-10, SEC-12). |
| `sql-string-building` `app.py:12`, `:18` (low) | **Confirmed** by reading | String-built SQL from URL param and JSON keys/values (SEC-17). |
| `html-sink` `static/main.js:5` (low) | **Confirmed** sink; exploitability **suspected** | Server response written via `innerHTML`; depends on what `/search` returns (SEC-19). |
| `browser-storage-token` `static/main.js:6` (low) | **Confirmed** | Token placed in `localStorage` (SEC-68). |
| manifest without lockfile `package.json` | **Confirmed** | No lockfile (SEC-62). |

## Findings found by reading code that the scanner missed (false negatives)

| ID | Severity | Confidence | Location | Evidence | Fix (proposed, not applied) |
| --- | --- | --- | --- | --- | --- |
| SEC-05 / SEC-70 | High | confirmed (code reading) | `app.py:9-13`, `:25-26` | `/api/orders/<id>` and `/admin` have no authentication or authorization decorator. | Default-deny auth middleware; explicit public-route list. |
| SEC-33 / SEC-06 | High | confirmed (code reading) | `app.py:9-13` | Order fetched by ID with no ownership predicate. | Scope query by session user; two-account test. |
| SEC-51 | High | confirmed (code reading) | `app.py:16-20` | JSON keys become SQL column names: mass assignment and injection (also SEC-17). | Allowlisted fields and parameterised update. |
| SEC-03 | Medium | confirmed (code reading) | `app.py:6` | `SECRET_KEY` is a literal. **Scanner missed it** because the key is written as `config["SECRET_KEY"]`. | Load from environment; fail if unset; rotate. |

The miss above is a concrete example of why pattern scanning cannot replace review.

## Items needing human decision

- Whether `.env` is deployed to any web root, and whether the demo credential value ever existed outside this repository.
- Whether `/admin` is intended to be public.

## Verification status

| Check | Status |
| --- | --- |
| Scanner re-run after fixes | unverified: no fixes applied |
| Cross-account authorization test | unverified: not written |
| Injection regression tests | unverified: not written |
| Dependency audit | unavailable: no lockfile |

## Residual risk

Everything above remains open. This report does not establish that any other part of the application is secure.
