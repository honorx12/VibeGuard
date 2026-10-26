import copy
import json
from pathlib import Path

import build_registry as br
import validate_skills as vs

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "registry"

def load(name):
    return json.loads((REG / name).read_text())

def test_committed_registry_valid():
    assert vs.validate_registry(REG) == []

def test_registry_is_current():
    assert br.main(["--check", "--root", str(ROOT)]) == 0

def test_index_covers_every_skill():
    idx = load("skills-index.json")
    names = {s["name"] for s in idx["skills"]}
    assert names == {p.parent.name for p in vs.find_skill_files(ROOT / "skills")}
    assert all(s["review_status"] == "first-party" for s in idx["skills"])

def _write(tmp_path, doc, name="skills-index.json"):
    reg = tmp_path / "registry"
    reg.mkdir(exist_ok=True)
    (reg / "schema.json").write_text((REG / "schema.json").read_text())
    (reg / name).write_text(json.dumps(doc))
    return reg

def test_missing_required_field_rejected(tmp_path):
    doc = load("skills-index.json")
    del doc["skills"][0]["license"]
    assert any("license" in e for e in vs.validate_registry(_write(tmp_path, doc)))

def test_bad_status_and_date_rejected(tmp_path):
    doc = load("skills-index.json")
    doc["skills"][0]["review_status"] = "trusted-by-scanner"
    doc["skills"][1]["last_reviewed"] = "yesterday"
    errs = vs.validate_registry(_write(tmp_path, doc))
    assert any("review_status" in e for e in errs) and any("last_reviewed" in e for e in errs)

def test_duplicate_ids_rejected(tmp_path):
    doc = load("skills-index.json")
    doc["skills"].append(copy.deepcopy(doc["skills"][0]))
    assert any("duplicate" in e for e in vs.validate_registry(_write(tmp_path, doc)))

def test_additional_properties_rejected(tmp_path):
    doc = load("skills-index.json")
    doc["skills"][0]["surprise"] = 1
    assert vs.validate_registry(_write(tmp_path, doc))

def test_invalid_json_reported(tmp_path):
    reg = _write(tmp_path, {})
    (reg / "skills-index.json").write_text("{not json")
    assert any("invalid JSON" in e for e in vs.validate_registry(reg))

def test_missing_schema_reported(tmp_path):
    assert vs.validate_registry(tmp_path)

def test_external_candidates_valid_and_never_auto_approved():
    ext = load("external-candidates.json")
    assert ext["skills"], "external candidate catalogue should not be empty"
    for s in ext["skills"]:
        assert s["review_status"] in {"pending-human-review", "link-only", "approved", "rejected"}
        if s["review_status"] == "approved":
            assert s["last_reviewed"]
    assert vs.validate_registry(REG, files=("external-candidates.json",)) == []

def test_stale_index_detected(tmp_path):
    import shutil
    for d in ("skills", "registry", "docs"):
        if (ROOT / d).exists():
            shutil.copytree(ROOT / d, tmp_path / d)
    assert br.main(["--check", "--root", str(tmp_path)]) == 0
    p = tmp_path / "registry" / "skills-index.json"
    p.write_text(p.read_text().replace("first-party", "first-party ", 1))
    assert br.main(["--check", "--root", str(tmp_path)]) == 1
