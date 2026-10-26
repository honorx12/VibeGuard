#!/usr/bin/env python3
"""Validate skills, coverage mapping and registry files.

Checks (see docs/SKILL_AUTHORING_GUIDE.md): Agent Skills frontmatter rules from
https://agentskills.io/specification, repository conventions (required sections,
line budget), duplicate names, local references, related-skill links, coverage
mapping integrity and registry schema validity. Exit code 1 on any error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("PyYAML is required: pip install -r requirements.txt\n"); sys.exit(2)

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
REQUIRED_SECTIONS = ["Objective", "When to Use", "Scope", "Workflow", "Verification", "Limitations", "Output Format"]
MAX_BODY_LINES = 500
EXPECTED_COUNTS = {"security": 70, "ux": 20, "production": 27}
ID_PREFIX = {"security": "SEC", "ux": "UX", "production": "PROD"}
REPO_PATH_RE = re.compile(r"(?<![\w./-])((?:scripts|docs|registry|agents|examples|tests)/[\w./-]+\.[A-Za-z0-9]+)")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")

class FrontmatterError(ValueError):
    pass

def parse_frontmatter(text: str):
    if not text.startswith("---"):
        raise FrontmatterError("file must start with '---' YAML frontmatter")
    parts = text.split("\n")
    end = next((i for i in range(1, len(parts)) if parts[i].strip() == "---"), None)
    if end is None:
        raise FrontmatterError("frontmatter is not closed with '---'")
    try:
        data = yaml.safe_load("\n".join(parts[1:end]))
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter must be a YAML mapping")
    return data, "\n".join(parts[end + 1:])

def find_skill_files(skills_dir: Path):
    return sorted(skills_dir.rglob("SKILL.md"))

def validate_skill(path: Path, repo_root: Path, known_names: set | None = None) -> list[str]:
    errs: list[str] = []
    rel = path.relative_to(repo_root) if path.is_relative_to(repo_root) else path
    def err(msg): errs.append(f"{rel}: {msg}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{rel}: cannot read file ({exc})"]
    try:
        fm, body = parse_frontmatter(text)
    except FrontmatterError as exc:
        return [f"{rel}: {exc}"]
    for k in fm:
        if k not in ALLOWED_KEYS:
            err(f"unknown frontmatter field '{k}' (allowed: {', '.join(sorted(ALLOWED_KEYS))})")
    name = fm.get("name")
    if not isinstance(name, str) or not name:
        err("missing required 'name'")
    else:
        if len(name) > 64: err(f"name longer than 64 characters ({len(name)})")
        if not NAME_RE.match(name): err("name must be lowercase letters, numbers and single hyphens, not starting/ending with a hyphen")
        if path.parent.name != name: err(f"directory name '{path.parent.name}' does not match name '{name}'")
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        err("missing or empty 'description'")
    elif len(desc) > 1024:
        err(f"description longer than 1024 characters ({len(desc)})")
    if "license" in fm and not isinstance(fm["license"], str): err("license must be a string")
    if "compatibility" in fm and (not isinstance(fm["compatibility"], str) or len(fm["compatibility"]) > 500):
        err("compatibility must be a string of at most 500 characters")
    if "allowed-tools" in fm and not isinstance(fm["allowed-tools"], str): err("allowed-tools must be a space-separated string")
    if "metadata" in fm:
        md = fm["metadata"]
        if not isinstance(md, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in md.items()):
            err("metadata must be a mapping of string keys to string values")
    if not body.strip():
        err("body is empty")
    headings = {m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", body, re.M)}
    for sec in REQUIRED_SECTIONS:
        if sec not in headings: err(f"missing required section '## {sec}'")
    if len(body.splitlines()) > MAX_BODY_LINES:
        err(f"body longer than {MAX_BODY_LINES} lines; move detail into references/")
    # local markdown links (relative to the skill file)
    for link in LINK_RE.findall(body):
        if re.match(r"^[a-z]+:", link) or link.startswith("#"):
            continue
        if not (path.parent / link).exists():
            err(f"broken local link '{link}'")
    # repo path mentions (scripts/, docs/, ...) relative to the repository root
    for ref in set(REPO_PATH_RE.findall(body)):
        if not (repo_root / ref).exists():
            err(f"referenced repository file does not exist: {ref}")
    # related skills
    if known_names is not None:
        m = re.search(r"^## Related Skills\s*\n(.*?)(?=^## |\Z)", body, re.M | re.S)
        if m:
            for rn in re.findall(r"`([^`]+)`", m.group(1)):
                if rn not in known_names: err(f"related skill '{rn}' does not exist")
    return errs

def validate_skills_tree(skills_dir: Path, repo_root: Path) -> list[str]:
    errs: list[str] = []
    files = find_skill_files(skills_dir)
    if not files:
        return [f"no SKILL.md files found under {skills_dir}"]
    names: dict[str, Path] = {}
    for f in files:
        try:
            fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
            n = fm.get("name")
        except (FrontmatterError, OSError, UnicodeDecodeError):
            n = None
        if isinstance(n, str):
            if n in names:
                errs.append(f"duplicate skill name '{n}': {names[n]} and {f}")
            names[n] = f
    known = set(names)
    for f in files:
        errs += validate_skill(f, repo_root, known)
    return errs

def validate_coverage(cov_path: Path, skills_dir: Path) -> list[str]:
    errs: list[str] = []
    if not cov_path.exists():
        return [f"coverage file missing: {cov_path}"]
    try:
        cov = json.loads(cov_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{cov_path}: invalid JSON ({exc})"]
    texts: dict[str, str] = {}
    for f in find_skill_files(skills_dir):
        try:
            fm, body = parse_frontmatter(f.read_text(encoding="utf-8"))
            texts[fm.get("name")] = body
        except Exception:
            pass
    for group, expected in EXPECTED_COUNTS.items():
        items = cov.get(group)
        if not isinstance(items, list):
            errs.append(f"coverage group '{group}' missing"); continue
        if len(items) != expected:
            errs.append(f"coverage group '{group}' has {len(items)} items, expected {expected}")
        ids = [i.get("id") for i in items]
        if len(set(ids)) != len(ids): errs.append(f"duplicate IDs in coverage group '{group}'")
        for it in items:
            iid = it.get("id", "?")
            if not str(iid).startswith(ID_PREFIX[group] + "-"): errs.append(f"{iid}: wrong prefix for group {group}")
            for key in ("title", "primary_skill", "verification"):
                if not it.get(key): errs.append(f"{iid}: missing '{key}'")
            for sk in [it.get("primary_skill")] + list(it.get("secondary_skills", [])):
                if sk not in texts: errs.append(f"{iid}: references unknown skill '{sk}'")
            prim = it.get("primary_skill")
            if prim in texts and not re.search(rf"^### {re.escape(iid)} ", texts[prim], re.M):
                errs.append(f"{iid}: not documented in primary skill '{prim}'")
    return errs

def validate_registry(registry_dir: Path, files=("skills-index.json", "external-candidates.json")) -> list[str]:
    errs: list[str] = []
    schema_path = registry_dir / "schema.json"
    try:
        import jsonschema
    except ImportError:  # pragma: no cover
        return ["jsonschema is required: pip install -r requirements.txt"]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        return [f"{schema_path}: unusable schema ({exc})"]
    validator = jsonschema.Draft202012Validator(schema)
    for fname in files:
        p = registry_dir / fname
        if not p.exists():
            if fname == "skills-index.json": errs.append(f"{p}: missing")
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errs.append(f"{p}: invalid JSON ({exc})"); continue
        for e in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            loc = "/".join(str(x) for x in e.path) or "<root>"
            errs.append(f"{fname}: {loc}: {e.message}")
        ids = [s.get("id") for s in data.get("skills", []) if isinstance(s, dict)]
        if len(ids) != len(set(ids)): errs.append(f"{fname}: duplicate registry ids")
    return errs

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validate skills, coverage mapping and registry.")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent), help="repository root")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    errs = validate_skills_tree(root / "skills", root)
    errs += validate_coverage(root / "registry" / "coverage.json", root / "skills")
    errs += validate_registry(root / "registry")
    n = len(find_skill_files(root / "skills"))
    if errs:
        print(f"FAILED: {len(errs)} problem(s) across {n} skill file(s)")
        for e in errs: print(f"  - {e}")
        return 1
    print(f"OK: {n} skills, coverage mapping and registry validated")
    return 0

if __name__ == "__main__":
    sys.exit(main())
