#!/usr/bin/env python3
"""Catalogue publicly available agent skills (GitHub repository search API only).

Safe by design:
  * Uses the documented GitHub REST API (no scraping, no access-control bypass).
  * Writes METADATA ONLY to registry/external-candidates.json. It never copies skill
    files into skills/, never installs, never executes third-party content.
  * Optional --inspect fetches SKILL.md text (size-capped) and runs heuristic checks.
    Heuristics are indicators for a human reviewer, never approval.
  * Every candidate starts as 'pending-human-review' (or 'link-only' when the licence
    does not clearly permit redistribution).
Optional GITHUB_TOKEN env var raises API rate limits; it is only sent to api.github.com.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
USER_AGENT = "ai-web-quality-skills-discovery/0.1 (+metadata-only)"
DEFAULT_QUERIES = [
    "topic:agent-skills security",
    "topic:agent-skills accessibility",
    "topic:agent-skills code-review",
    "topic:agent-skills production",
    "SKILL.md security audit in:readme",
]
PERMISSIVE_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "CC0-1.0", "Unlicense", "CC-BY-4.0", "0BSD"}
MAX_TEXT_BYTES = 100_000
MAX_SKILL_FILES_PER_REPO = 5

SUSPICIOUS = [
    ("pipe-to-shell", re.compile(r"(?i)\b(?:curl|wget)\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba|z)?sh\b")),
    ("encoded-execution", re.compile(r"(?i)(?:base64\s+(?:-d|--decode)|atob\(|b64decode)[^\n]*(?:\|\s*(?:ba)?sh|eval|exec)")),
    ("instruction-override", re.compile(r"(?i)ignore\s+(?:all\s+|any\s+)?(?:previous|prior|above)\s+(?:instructions|rules|messages)")),
    ("concealment-from-user", re.compile(r"(?i)do\s+not\s+(?:tell|inform|mention|show|reveal)[^\n]{0,40}\buser\b")),
    ("credential-file-access", re.compile(r"(?i)(?:~|\$HOME)?/?\.(?:ssh|aws|gnupg|kube)/|\.env\b|id_rsa|credentials\.json")),
    ("data-exfiltration", re.compile(r"(?i)\b(?:curl|wget|Invoke-WebRequest|requests\.post|fetch)\b[^\n]*(?:\$\{?\w*(?:KEY|TOKEN|SECRET|PASSWORD)\w*\}?|\benv\b|--data|-d\s)")),
    ("destructive-command", re.compile(r"\brm\s+-rf\s+(?:/|~|\$HOME)|\bmkfs\b|\bdd\s+if=.*of=/dev/")),
    ("safety-bypass", re.compile(r"(?i)(?:disable|bypass|skip|turn\s+off)\s+(?:all\s+)?(?:safety|security|permission|approval|confirmation)")),
    ("privilege-escalation", re.compile(r"\bsudo\b|\bchmod\s+(?:\+s|777)\b")),
    ("hidden-unicode", re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]")),
    ("hidden-html-comment-instructions", re.compile(r"(?is)<!--[^>]*(?:ignore|instruction|you must|assistant)[^>]*-->")),
]
CATEGORY_KEYWORDS = [
    ("security", ("security", "secret", "vulnerab", "owasp", "pentest", "audit")),
    ("frontend", ("accessib", "a11y", "frontend", "css", "ui ", "ux")),
    ("production", ("production", "seo", "performance", "deploy", "launch")),
    ("engineering", ("code review", "code-review", "testing", "refactor", "review")),
]

class DiscoveryError(Exception):
    pass

def _request(url: str, token: str | None, timeout: float, accept: str) -> bytes:
    headers = {"User-Agent": USER_AGENT, "Accept": accept}
    if token and urllib.parse.urlparse(url).hostname == "api.github.com":
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (https URLs only, fixed hosts)
            return resp.read(MAX_TEXT_BYTES * 20)
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 429):
            raise DiscoveryError(f"rate limited or forbidden (HTTP {exc.code}) for {url}; set GITHUB_TOKEN or retry later") from exc
        raise DiscoveryError(f"HTTP {exc.code} for {url}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise DiscoveryError(f"network error for {url}: {exc}") from exc

def fetch_json(url: str, token: str | None = None, timeout: float = 15.0):
    if not url.startswith("https://"):
        raise DiscoveryError("only https URLs are allowed")
    raw = _request(url, token, timeout, "application/vnd.github+json")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DiscoveryError(f"malformed JSON from {url}: {exc}") from exc

def fetch_text(url: str, timeout: float = 15.0) -> str:
    if not url.startswith("https://"):
        raise DiscoveryError("only https URLs are allowed")
    return _request(url, None, timeout, "text/plain")[:MAX_TEXT_BYTES].decode("utf-8", errors="replace")

def search_repositories(query: str, fetch=fetch_json, per_page: int = 10, token: str | None = None) -> list[dict]:
    url = f"{API}/search/repositories?q={urllib.parse.quote(query)}&per_page={per_page}&sort=updated&order=desc"
    data = fetch(url, token) if fetch is fetch_json else fetch(url)
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise DiscoveryError(f"unexpected response shape for query {query!r}")
    return data["items"]

def classify(text: str) -> str:
    t = text.lower()
    for cat, kws in CATEGORY_KEYWORDS:
        if any(k in t for k in kws):
            return cat
    return "external-unclassified"

def normalize_repo(item: dict, today: str):
    """Return a registry entry or None if essential metadata is missing."""
    if not isinstance(item, dict):
        return None
    full, url = item.get("full_name"), item.get("html_url")
    if not isinstance(full, str) or "/" not in full or not isinstance(url, str) or not url.startswith("https://"):
        return None
    lic = (item.get("license") or {}).get("spdx_id") if isinstance(item.get("license"), dict) else None
    lic = lic if lic and lic not in ("NOASSERTION", "null") else "UNKNOWN"
    desc = (item.get("description") or "")[:1024]
    permissive = lic in PERMISSIVE_LICENSES
    flags = [] if permissive else ["licence-unclear-or-restrictive: catalogue and link only"]
    owner = (item.get("owner") or {}).get("login") if isinstance(item.get("owner"), dict) else None
    return {
        "id": f"github/{full.lower()}", "name": item.get("name") or full.split("/")[-1], "description": desc,
        "category": classify(f"{item.get('name','')} {desc}"), "source_url": url, "repository_url": url,
        "revision": "unresolved", "license": lic, "compatibility": ["unverified"], "last_reviewed": None,
        "review_status": "pending-human-review" if permissive else "link-only",
        "risk_notes": "Not reviewed. Do not install or execute until a human has read every file." ,
        "related_skills": [], "author": owner, "retrieved_at": today,
        "redistribution": "permitted-by-license" if permissive else "link-only", "flags": flags,
        "_pushed_at": item.get("pushed_at"), "_default_branch": item.get("default_branch"),
    }

def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))

def dedupe(entries: list[dict], threshold: float = 0.92):
    """Remove exact (same repo) and near-duplicate (same name + very similar description) entries."""
    unique, dups = [], []
    for e in entries:
        hit = None
        for u in unique:
            if u["id"] == e["id"]:
                hit = (u, "same-repository"); break
            if _tokens(u["name"]) == _tokens(e["name"]) and u["description"] and e["description"] and \
               difflib.SequenceMatcher(None, u["description"].lower(), e["description"].lower()).ratio() >= threshold:
                hit = (u, "near-duplicate"); break
        if hit:
            dups.append({"id": e["id"], "duplicate_of": hit[0]["id"], "kind": hit[1]})
        else:
            unique.append(e)
    return unique, dups

def inspect_text(text: str) -> list[str]:
    """Heuristic indicators only. Empty list does NOT mean safe."""
    return [name for name, rx in SUSPICIOUS if rx.search(text)]

def inspect_repo(entry: dict, fetch=fetch_json, fetch_raw=fetch_text, token: str | None = None) -> dict:
    """Read SKILL.md text (never execute). Adds flags to the entry; may raise DiscoveryError."""
    full = entry["id"].split("github/", 1)[1]
    branch = entry.get("_default_branch") or "HEAD"
    tree = fetch(f"{API}/repos/{full}/git/trees/{urllib.parse.quote(branch)}?recursive=1", token) if fetch is fetch_json \
        else fetch(f"{API}/repos/{full}/git/trees/{urllib.parse.quote(branch)}?recursive=1")
    paths = [t["path"] for t in tree.get("tree", []) if isinstance(t, dict) and str(t.get("path", "")).endswith("SKILL.md")]
    flags = set()
    bundled_scripts = [t["path"] for t in tree.get("tree", []) if isinstance(t, dict) and re.search(r"(?:^|/)scripts/", str(t.get("path", "")))]
    for p in paths[:MAX_SKILL_FILES_PER_REPO]:
        text = fetch_raw(f"{RAW}/{full}/{urllib.parse.quote(branch)}/{urllib.parse.quote(p)}")
        flags.update(inspect_text(text))
    entry["flags"] = sorted(set(entry.get("flags", [])) | {f"heuristic:{f}" for f in flags} |
                            {f"skill-files-inspected:{min(len(paths), MAX_SKILL_FILES_PER_REPO)}"} |
                            ({"bundled-scripts-present: review manually, never execute during review"} if bundled_scripts else set()))
    if flags:
        entry["flags"].append("manual-review-required")
        entry["risk_notes"] = "Heuristic indicators found: " + ", ".join(sorted(flags)) + ". Human review required; do not install."
    if not paths:
        entry["flags"].append("no-SKILL.md-found")
    return entry

def resolve_revision(entry: dict, fetch=fetch_json, token: str | None = None) -> None:
    full = entry["id"].split("github/", 1)[1]
    branch = entry.get("_default_branch") or "HEAD"
    data = fetch(f"{API}/repos/{full}/commits/{urllib.parse.quote(branch)}", token) if fetch is fetch_json else fetch(f"{API}/repos/{full}/commits/{urllib.parse.quote(branch)}")
    sha = data.get("sha") if isinstance(data, dict) else None
    if isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha):
        entry["revision"] = sha

def merge_with_existing(new: list[dict], existing: list[dict]) -> list[dict]:
    """Preserve human review decisions and prior records."""
    by_id = {e["id"]: e for e in existing}
    for e in new:
        old = by_id.get(e["id"])
        if old:
            if old.get("review_status") in ("approved", "rejected"):
                for k in ("review_status", "last_reviewed", "risk_notes", "compatibility", "related_skills"):
                    e[k] = old.get(k, e[k])
            by_id[e["id"]] = e
        else:
            by_id[e["id"]] = e
    return sorted(by_id.values(), key=lambda x: x["id"])

def run(queries, fetch=fetch_json, fetch_raw=fetch_text, token=None, per_page=10, inspect=False,
        revisions=False, today=None, sleep=0.0, existing=None):
    today = today or dt.date.today().isoformat()
    collected, errors = [], []
    ok_queries = 0
    for i, q in enumerate(queries):
        if i and sleep: time.sleep(sleep)
        try:
            items = search_repositories(q, fetch, per_page, token)
            ok_queries += 1
        except DiscoveryError as exc:
            errors.append(str(exc)); continue
        for it in items:
            e = normalize_repo(it, today)
            if e is None:
                errors.append(f"skipped malformed result in query {q!r}"); continue
            collected.append(e)
    unique, dups = dedupe(collected)
    rate_limited = False
    for e in unique:
        for step, enabled in ((inspect_repo, inspect), (resolve_revision, revisions)):
            if not enabled: continue
            if rate_limited:
                e.setdefault("flags", []).append("inspection-skipped-rate-limited"); break
            try:
                if step is inspect_repo: inspect_repo(e, fetch, fetch_raw, token)
                else: resolve_revision(e, fetch, token)
            except DiscoveryError as exc:
                e.setdefault("flags", []).append("inspection-failed")
                if "rate limited" in str(exc):
                    rate_limited = True
                    errors.append(f"{e['id']}: {exc}; skipping remaining per-repository calls")
                else:
                    errors.append(f"{e['id']}: {exc}")
    for e in unique:
        e.pop("_pushed_at", None); e.pop("_default_branch", None)
        e["flags"] = sorted(set(e.get("flags", [])))
    merged = merge_with_existing(unique, existing or [])
    return {"schema_version": 1, "generated_by": "scripts/discover_skills.py", "retrieved_at": today, "skills": merged}, dups, errors, ok_queries

def render_report(doc: dict, dups: list, errors: list) -> str:
    out = ["# Discovery Review Report", "", f"Retrieved: {doc['retrieved_at']}  Candidates: {len(doc['skills'])}",
           "", "All entries are metadata only. Nothing was installed or executed. A human must review each before any adoption.", ""]
    for s in doc["skills"]:
        out += [f"## {s['id']}", f"- source: {s['source_url']}", f"- licence: {s['license']} ({s['redistribution']})",
                f"- status: {s['review_status']}", f"- revision: {s['revision']}", f"- flags: {', '.join(s.get('flags', [])) or 'none'}",
                f"- note: {s['risk_notes']}", ""]
    if dups: out += ["## Duplicates removed", ""] + [f"- {d['id']} ({d['kind']} of {d['duplicate_of']})" for d in dups] + [""]
    if errors: out += ["## Errors and gaps", ""] + [f"- {e}" for e in errors] + [""]
    return "\n".join(out)

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--query", action="append", help="GitHub repository search query (repeatable); default set used if omitted")
    ap.add_argument("--per-page", type=int, default=10)
    ap.add_argument("--inspect", action="store_true", help="fetch SKILL.md text for heuristic checks (read-only)")
    ap.add_argument("--resolve-revision", action="store_true", help="record head commit SHA of default branch")
    ap.add_argument("--output", default=str(Path(__file__).resolve().parent.parent / "registry" / "external-candidates.json"))
    ap.add_argument("--report", help="also write a markdown review report to this path")
    ap.add_argument("--sleep", type=float, default=2.0, help="seconds between queries (politeness)")
    ap.add_argument("--dry-run", action="store_true", help="print JSON; write nothing")
    args = ap.parse_args(argv)
    out_path = Path(args.output)
    existing = []
    if out_path.exists():
        try: existing = json.loads(out_path.read_text(encoding="utf-8")).get("skills", [])
        except (OSError, json.JSONDecodeError): existing = []
    token = os.environ.get("GITHUB_TOKEN")
    doc, dups, errors, ok = run(args.query or DEFAULT_QUERIES, token=token, per_page=args.per_page, inspect=args.inspect,
                                revisions=args.resolve_revision, sleep=args.sleep, existing=existing)
    for e in errors: print(f"warning: {e}", file=sys.stderr)
    if ok == 0:
        print("error: all queries failed; nothing written", file=sys.stderr); return 1
    text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    if args.dry_run:
        sys.stdout.write(text); return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    if args.report: Path(args.report).write_text(render_report(doc, dups, errors), encoding="utf-8")
    print(f"Wrote {out_path} ({len(doc['skills'])} candidates, {len(dups)} duplicates removed, {len(errors)} warnings)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
