from pathlib import Path

import pytest

import validate_skills as vs

ROOT = Path(__file__).resolve().parent.parent

GOOD_BODY = """
# Title

## Objective
x
## When to Use
x
## Scope
x
## Workflow
x
## Verification
x
## Limitations
x
## Output Format
x
## Related Skills
- `{related}`
"""

def make(tmp_path, name, fm_extra="", body=None, dirname=None, desc="Does a thing. Use when testing.", related="good-skill"):
    d = tmp_path / "skills" / "cat" / (dirname or name)
    d.mkdir(parents=True, exist_ok=True)
    fm = f"---\nname: {name}\ndescription: {desc}\n{fm_extra}---\n"
    (d / "SKILL.md").write_text(fm + (body if body is not None else GOOD_BODY.format(related=related)))
    return d / "SKILL.md"

def run(tmp_path):
    return vs.validate_skills_tree(tmp_path / "skills", tmp_path)

def test_repository_skills_are_valid():
    assert vs.validate_skills_tree(ROOT / "skills", ROOT) == []

def test_all_expected_skills_present():
    names = {p.parent.name for p in vs.find_skill_files(ROOT / "skills")}
    assert len(names) == 24
    assert {"security-audit", "secrets-detection", "skill-supply-chain-review", "production-readiness"} <= names

def test_valid_minimal_skill(tmp_path):
    make(tmp_path, "good-skill")
    assert run(tmp_path) == []

@pytest.mark.parametrize("bad", ["Bad-Name", "-lead", "trail-", "dou--ble", "under_score", "a" * 65])
def test_invalid_names_rejected(tmp_path, bad):
    make(tmp_path, bad, related="x")
    errs = run(tmp_path)
    assert any("name" in e for e in errs)

def test_directory_name_must_match(tmp_path):
    make(tmp_path, "good-skill", dirname="other-dir")
    assert any("does not match" in e for e in run(tmp_path))

def test_missing_description(tmp_path):
    p = make(tmp_path, "good-skill")
    p.write_text("---\nname: good-skill\n---\n" + GOOD_BODY.format(related="good-skill"))
    assert any("description" in e for e in run(tmp_path))

def test_description_too_long(tmp_path):
    make(tmp_path, "good-skill", desc="x" * 1025)
    assert any("1024" in e for e in run(tmp_path))

def test_unknown_frontmatter_field(tmp_path):
    make(tmp_path, "good-skill", fm_extra="color: red\n")
    assert any("unknown frontmatter field" in e for e in run(tmp_path))

def test_metadata_values_must_be_strings(tmp_path):
    make(tmp_path, "good-skill", fm_extra="metadata:\n  n: 5\n")
    assert any("metadata" in e for e in run(tmp_path))

def test_invalid_yaml_and_missing_frontmatter(tmp_path):
    p = make(tmp_path, "good-skill")
    p.write_text("---\nname: [unclosed\n---\nbody")
    assert any("invalid YAML" in e for e in run(tmp_path))
    p.write_text("no frontmatter")
    assert any("must start with" in e for e in run(tmp_path))
    p.write_text("---\nname: x\n")
    assert any("not closed" in e for e in run(tmp_path))

def test_duplicate_names(tmp_path):
    make(tmp_path, "good-skill")
    d = tmp_path / "skills" / "other" / "good-skill"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: good-skill\ndescription: dup\n---\n" + GOOD_BODY.format(related="good-skill"))
    assert any("duplicate skill name" in e for e in run(tmp_path))

def test_missing_required_section(tmp_path):
    make(tmp_path, "good-skill", body="# T\n\n## Objective\nx\n")
    errs = run(tmp_path)
    assert any("missing required section '## Verification'" in e for e in errs)

def test_broken_local_link_and_repo_reference(tmp_path):
    body = GOOD_BODY.format(related="good-skill") + "\nSee [ref](references/nope.md) and `scripts/missing_tool.py`.\n"
    make(tmp_path, "good-skill", body=body)
    errs = run(tmp_path)
    assert any("broken local link" in e for e in errs)
    assert any("scripts/missing_tool.py" in e for e in errs)

def test_unknown_related_skill(tmp_path):
    make(tmp_path, "good-skill", related="ghost-skill")
    assert any("ghost-skill" in e for e in run(tmp_path))

def test_body_line_budget(tmp_path):
    body = GOOD_BODY.format(related="good-skill") + "\n".join(["line"] * 600)
    make(tmp_path, "good-skill", body=body)
    assert any("500 lines" in e for e in run(tmp_path))

def test_unreadable_file_reported(tmp_path):
    p = make(tmp_path, "good-skill")
    p.write_bytes(b"\xff\xfe\x00bad")
    assert run(tmp_path)  # reports instead of crashing

def test_empty_tree(tmp_path):
    (tmp_path / "skills").mkdir()
    assert any("no SKILL.md" in e for e in vs.validate_skills_tree(tmp_path / "skills", tmp_path))

def test_cli_exit_codes(tmp_path):
    assert vs.main(["--root", str(ROOT)]) == 0
    (tmp_path / "skills").mkdir()
    assert vs.main(["--root", str(tmp_path)]) == 1
