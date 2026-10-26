#!/usr/bin/env python3
"""Conservative local project inventory and security-pattern scan.

Reports *candidates* only. Never prints matched text or secret values, never
modifies the target, never makes network requests. It is NOT a replacement for
dedicated secret scanners, SAST, dependency auditing, dynamic testing or
expert review. See docs/SECURITY_MODEL.md for false-positive/negative notes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path

DEFAULT_SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "venv", ".venv", "env", "__pycache__", "dist", "build",
    ".next", ".nuxt", ".svelte-kit", "target", "vendor", "coverage", ".tox", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", ".idea", ".gradle", "bower_components", ".terraform", "site-packages",
}
LOCKFILE_NAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "poetry.lock", "uv.lock",
                  "Pipfile.lock", "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock"}
MANIFESTS = {  # manifest -> acceptable lockfiles (same directory)
    "package.json": {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb"},
    "pyproject.toml": {"poetry.lock", "uv.lock", "requirements.lock", "requirements-lock.txt"},
    "requirements.txt": {"requirements.lock", "requirements-lock.txt", "poetry.lock", "uv.lock", "Pipfile.lock"},
    "Pipfile": {"Pipfile.lock"},
    "Cargo.toml": {"Cargo.lock"},
    "go.mod": {"go.sum"},
    "Gemfile": {"Gemfile.lock"},
    "composer.json": {"composer.lock"},
}
PUBLIC_DIR_NAMES = {"public", "static", "www", "wwwroot", "html", "web", "dist", "build", "assets"}
EXAMPLE_SUFFIXES = (".example", ".sample", ".template", ".dist", ".tpl")
MAX_FILE_BYTES = 1_000_000
MAX_LINE_CHARS = 4000
PLACEHOLDER_RE = re.compile(r"(?i)(?:example|placeholder|changeme|change_me|your[_-]|<[^>]+>|\$\{|\{\{|xxx+|\*{3,}|dummy|sample|fake|test)")

@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    pattern: re.Pattern
    coverage: tuple
    confidence: str          # base confidence: low | medium
    secret: bool = False     # True: value is sensitive and must be redacted
    value_group: int = 0     # group holding the value (for placeholder check)

def R(id_, title, rx, cov, conf, secret=False, group=0):
    return Rule(id_, title, re.compile(rx), tuple(cov), conf, secret, group)

RULES = [
    R("aws-access-key-id", "AWS access key ID pattern", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b", ["SEC-03"], "medium", True),
    R("private-key-block", "Private key block", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----", ["SEC-03"], "medium", True),
    R("github-token", "GitHub token pattern", r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", ["SEC-03"], "medium", True),
    R("slack-token", "Slack token pattern", r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b", ["SEC-03"], "medium", True),
    R("stripe-live-key", "Stripe live key pattern", r"\b(?:sk|rk)_live_[0-9a-zA-Z]{16,}\b", ["SEC-03", "SEC-14"], "medium", True),
    R("google-api-key", "Google API key pattern", r"\bAIza[0-9A-Za-z_\-]{35}\b", ["SEC-03", "SEC-14"], "low", True),
    R("jwt-like-token", "JWT-like token literal", r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b", ["SEC-03", "SEC-26"], "low", True),
    R("db-url-with-password", "Database URL with embedded password",
      r"\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|amqps?|mssql)://[^\s:/@'\"]+:([^\s@'\"]+)@", ["SEC-01", "SEC-03"], "medium", True, 1),
    R("default-credential-literal", "Default-looking credential literal",
      r"(?i)\b(?:password|passwd|pwd)\b[\"']?\s*[:=]\s*[\"'](admin|password|changeme|123456|root|letmein|default)[\"']", ["SEC-30"], "medium", True, 1),
    R("generic-secret-assignment", "Secret-like assignment with literal value",
      r"(?i)[\w-]*(?:api[_-]?key|secret|token|passwd|password|private[_-]?key|access[_-]?key)[\w-]*[\"']?\s*[:=]\s*[\"']([^\"'\s]{8,})[\"']",
      ["SEC-03"], "low", True, 1),
    R("weak-jwt-secret", "Weak or default JWT secret literal",
      r"(?i)jwt[_-]?secret[\"']?\s*[:=]\s*[\"'](?:secret|changeme|password|jwt_secret|supersecret|123456|your-256-bit-secret)[\"']", ["SEC-26"], "medium", True),
    R("public-env-secret-name", "Client-exposed env var name suggests a secret",
      r"\b(?:NEXT_PUBLIC_|VITE_|REACT_APP_|NUXT_PUBLIC_|EXPO_PUBLIC_|GATSBY_)\w*(?:SECRET|PRIVATE|PASSWORD|SERVICE_ROLE|TOKEN)\w*", ["SEC-14"], "low"),
    R("debug-enabled", "Debug setting enabled",
      r"(?i)(?:\bDEBUG\s*[:=]\s*(?:True|true|1)\b|app\.run\([^)]*debug\s*=\s*True|FLASK_DEBUG\s*=\s*1|display_errors\s*=\s*(?:On|1))", ["SEC-10", "SEC-12"], "low"),
    R("cors-wildcard", "Wildcard CORS configuration",
      r"(?i)(?:Access-Control-Allow-Origin[\"']?\s*[:,=]\s*[\"']?\*|\borigin\s*:\s*[\"']\*[\"']|allow_origins\s*=\s*\[\s*[\"']\*[\"']|CORS_ORIGIN_ALLOW_ALL\s*=\s*True)", ["SEC-27"], "low"),
    R("tls-verification-disabled", "TLS verification disabled",
      r"(?i)(?:\bverify\s*=\s*False\b|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED[\"']?\s*[:=]\s*[\"']?0)", ["SEC-48", "SEC-63"], "low"),
    R("shell-true", "Shell execution enabled", r"\bshell\s*=\s*True\b", ["SEC-52"], "low"),
    R("unsafe-deserialization", "Potentially unsafe deserializer", r"\b(?:pickle\.loads?|yaml\.load|marshal\.loads?|unserialize)\s*\(", ["SEC-53"], "low"),
    R("sql-string-building", "SQL built from string formatting",
      r"(?i)\.(?:execute|query|raw)\(\s*(?:f[\"'][^\"']*\b(?:select|insert|update|delete)\b[^\"']*\{|[\"'][^\"']*\b(?:select|insert|update|delete)\b[^\"']*[\"']\s*(?:\+|%\s|\.format\())", ["SEC-17"], "low"),
    R("html-sink", "Unescaped HTML sink", r"(?:dangerouslySetInnerHTML|\.innerHTML\s*=|\bv-html\b|\|\s*safe\b)", ["SEC-19"], "low"),
    R("browser-storage-token", "Token-like value stored in browser storage",
      r"(?i)(?:localStorage|sessionStorage)\.setItem\(\s*[\"'][^\"']*(?:token|jwt|auth|session|secret)", ["SEC-68"], "low"),
]

@dataclass
class Finding:
    rule: str
    title: str
    file: str
    line: int
    confidence: str
    status: str = "candidate"
    coverage: list = field(default_factory=list)
    note: str = ""
    redacted_value: str = ""

def is_probably_binary(chunk: bytes) -> bool:
    return b"\x00" in chunk

def gitignore_patterns(root: Path):
    p = root / ".gitignore"
    try:
        return [ln.strip() for ln in p.read_text(errors="ignore").splitlines() if ln.strip() and not ln.startswith("#")]
    except OSError:
        return []

def env_ignored(patterns) -> bool:
    return any(p.lstrip("/").startswith(".env") or p in {"*.env", ".env*"} for p in patterns)

def classify_context(rel: Path) -> str:
    parts = {p.lower() for p in rel.parts[:-1]}
    name = rel.name.lower()
    if parts & {"test", "tests", "__tests__", "spec", "fixtures", "examples", "example", "docs", "doc"} or ".test." in name or name.startswith("test_"):
        return "test-or-doc"
    return "source"

def scan(target: Path, include_generated: bool = False, max_files: int = 50000):
    target = target.resolve()
    skip_dirs = set() if include_generated else DEFAULT_SKIP_DIRS
    inv = {"target": str(target), "files_scanned": 0, "files_skipped": [], "manifests": [], "missing_lockfiles": [],
           "lockfiles": [], "frameworks": [], "ci": [], "iac": [], "docker": False, "extensions": {}}
    findings: list[Finding] = []
    ignore_pats = gitignore_patterns(target)
    seen = 0
    for dirpath, dirnames, filenames in os.walk(target, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in skip_dirs)
        d = Path(dirpath)
        names = set(filenames)
        for mf, locks in MANIFESTS.items():
            if mf in names:
                rel = str((d / mf).relative_to(target))
                inv["manifests"].append(rel)
                if not (names & locks):
                    inv["missing_lockfiles"].append(rel)
        for ln in names & LOCKFILE_NAMES:
            inv["lockfiles"].append(str((d / ln).relative_to(target)))
        for fname in sorted(filenames):
            path = d / fname
            rel = path.relative_to(target)
            seen += 1
            if seen > max_files:
                inv["files_skipped"].append({"file": "*", "reason": f"max_files={max_files} reached"})
                return inv, findings
            if path.is_symlink():
                inv["files_skipped"].append({"file": str(rel), "reason": "symlink not followed"}); continue
            ext = path.suffix.lower() or fname
            inv["extensions"][ext] = inv["extensions"].get(ext, 0) + 1
            if fname == "Dockerfile" or fname.startswith("Dockerfile.") or fname in {"docker-compose.yml", "docker-compose.yaml"}:
                inv["docker"] = True
            if ext == ".tf": inv["iac"].append(str(rel))
            if ".github" in rel.parts and "workflows" in rel.parts: inv["ci"].append(str(rel))
            # env files
            if fname == ".env" or (fname.startswith(".env.") and not fname.endswith(EXAMPLE_SUFFIXES)):
                public = bool(set(p.lower() for p in rel.parts[:-1]) & PUBLIC_DIR_NAMES)
                ign = env_ignored(ignore_pats)
                note = ("inside a directory name commonly served publicly; " if public else "") + \
                       ("no .gitignore rule for .env* found" if not ign else ".gitignore appears to cover .env*")
                findings.append(Finding("env-file-present", "Environment file present", str(rel), 0,
                                        "medium" if (public or not ign) else "low", coverage=["SEC-02", "SEC-03"], note=note))
            if ext == ".map" and (set(p.lower() for p in rel.parts[:-1]) & PUBLIC_DIR_NAMES):
                findings.append(Finding("source-map-present", "Source map in public/build directory", str(rel), 0, "low",
                                        coverage=["SEC-36"], note="verify whether this file is deployed publicly"))
            if fname in LOCKFILE_NAMES or fname.endswith(".min.js"):
                continue  # lockfiles/minified bundles: inventory only, no content scan
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    inv["files_skipped"].append({"file": str(rel), "reason": "larger than size limit"}); continue
                with open(path, "rb") as fh:
                    head = fh.read(2048)
                    if is_probably_binary(head):
                        inv["files_skipped"].append({"file": str(rel), "reason": "binary"}); continue
                    data = head + fh.read()
            except OSError as exc:
                inv["files_skipped"].append({"file": str(rel), "reason": f"unreadable: {exc.__class__.__name__}"}); continue
            text = data.decode("utf-8", errors="ignore")
            inv["files_scanned"] += 1
            ctx = classify_context(rel)
            if fname == "package.json":
                for fw in ("react", "next", "vue", "nuxt", "svelte", "angular", "express", "fastify", "nestjs", "koa"):
                    if re.search(r'"(?:@?[\w/-]*)%s[\w/-]*"\s*:' % fw, text) and fw not in inv["frameworks"]:
                        inv["frameworks"].append(fw)
            if fname in {"requirements.txt", "pyproject.toml", "Pipfile"}:
                for fw in ("django", "flask", "fastapi", "starlette", "tornado", "pyramid"):
                    if re.search(r"(?i)\b%s\b" % fw, text) and fw not in inv["frameworks"]:
                        inv["frameworks"].append(fw)
            for lineno, line in enumerate(text.splitlines(), 1):
                line = line[:MAX_LINE_CHARS]
                matched_default_cred = False
                for rule in RULES:
                    if rule.id == "generic-secret-assignment" and matched_default_cred:
                        continue
                    m = rule.pattern.search(line)
                    if not m:
                        continue
                    value = m.group(rule.value_group) if rule.value_group else m.group(0)
                    if rule.id == "default-credential-literal":
                        matched_default_cred = True
                    conf = rule.confidence
                    notes = []
                    if ctx == "test-or-doc":
                        conf = "low"; notes.append("in test/doc/example path (likely fixture)")
                    if rule.secret and PLACEHOLDER_RE.search(value):
                        conf = "low"; notes.append("placeholder-like value (possible false positive)")
                    if rel.name.endswith(EXAMPLE_SUFFIXES):
                        conf = "low"; notes.append("example/template file")
                    findings.append(Finding(rule.id, rule.title, str(rel), lineno, conf, coverage=list(rule.coverage),
                                            note="; ".join(notes),
                                            redacted_value=f"[REDACTED len={len(value)}]" if rule.secret else ""))
    return inv, findings

def render_text(inv, findings) -> str:
    out = ["# Candidate findings (pattern matches, NOT confirmed vulnerabilities)", "",
           f"Target: {inv['target']}", f"Files scanned: {inv['files_scanned']}  skipped: {len(inv['files_skipped'])}", ""]
    out.append("## Inventory")
    out.append(f"- manifests: {', '.join(inv['manifests']) or 'none found'}")
    out.append(f"- lockfiles: {', '.join(sorted(inv['lockfiles'])) or 'none found'}")
    if inv["missing_lockfiles"]:
        out.append(f"- manifests without a lockfile in the same directory: {', '.join(inv['missing_lockfiles'])}  (SEC-62)")
    out.append(f"- frameworks (heuristic): {', '.join(inv['frameworks']) or 'unknown'}")
    out.append(f"- CI workflow files: {len(inv['ci'])}; IaC (.tf) files: {len(inv['iac'])}; Docker: {inv['docker']}")
    out += ["", "## Candidates"]
    if not findings:
        out.append("- none matched. This does not mean the project is free of issues.")
    for f in sorted(findings, key=lambda x: (x.file, x.line, x.rule)):
        loc = f"{f.file}:{f.line}" if f.line else f.file
        extra = f" {f.redacted_value}" if f.redacted_value else ""
        note = f" -- {f.note}" if f.note else ""
        out.append(f"- [{f.confidence}] {f.rule} @ {loc}{extra} -> {','.join(f.coverage)}{note}")
    if inv["files_skipped"]:
        out += ["", "## Skipped files"] + [f"- {s['file']}: {s['reason']}" for s in inv["files_skipped"][:50]]
    out += ["", "Limitations: regex candidates only; expect false positives and false negatives. Confirm each item by reading the code,",
            "and use dedicated tools (secret scanners, SAST, dependency audit) for real assurance."]
    return "\n".join(out) + "\n"

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Conservative local project inventory and security-pattern scan (candidates only).")
    ap.add_argument("target", help="directory to scan (read-only)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--output", help="write report to this file (must be outside the target)")
    ap.add_argument("--include-generated", action="store_true", help="also scan build/dependency directories")
    ap.add_argument("--fail-on-findings", action="store_true", help="exit 1 if any candidate is reported")
    args = ap.parse_args(argv)
    target = Path(args.target)
    if not target.is_dir():
        print(f"error: target is not a directory: {target}", file=sys.stderr); return 2
    if args.output:
        out_path = Path(args.output).resolve()
        try:
            out_path.relative_to(target.resolve())
            print("error: --output must be outside the target directory (scanner never writes into the target)", file=sys.stderr); return 2
        except ValueError:
            pass
    inv, findings = scan(target, include_generated=args.include_generated)
    report = (json.dumps({"inventory": inv, "findings": [asdict(f) for f in findings],
                          "disclaimer": "Candidates only; not confirmed vulnerabilities."}, indent=2) + "\n"
              if args.format == "json" else render_text(inv, findings))
    if args.output:
        try:
            Path(args.output).write_text(report)
        except OSError as exc:
            print(f"error: cannot write output: {exc}", file=sys.stderr); return 2
    else:
        sys.stdout.write(report)
    return 1 if (args.fail_on_findings and findings) else 0

if __name__ == "__main__":
    sys.exit(main())
