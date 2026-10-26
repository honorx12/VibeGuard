import hashlib
import json
from pathlib import Path

import scan_project as sp

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "tests" / "security-test-cases"

def tree_hash(path: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        h.update(str(p.relative_to(path)).encode())
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()

def rules(findings):
    return {f.rule for f in findings}

def test_vulnerable_fixture_candidates_detected():
    inv, findings = sp.scan(CASES / "vulnerable-app")
    got = rules(findings)
    expected = {"db-url-with-password", "weak-jwt-secret", "default-credential-literal", "debug-enabled", "sql-string-building",
                "shell-true", "unsafe-deserialization", "html-sink", "browser-storage-token", "public-env-secret-name",
                "cors-wildcard", "env-file-present", "generic-secret-assignment"}
    assert expected <= got, expected - got
    assert "express" in inv["frameworks"] and "react" in inv["frameworks"]
    assert any("package.json" in m for m in inv["missing_lockfiles"])

def test_all_findings_labelled_candidates():
    _, findings = sp.scan(CASES / "vulnerable-app")
    assert findings and all(f.status == "candidate" for f in findings)
    text = sp.render_text(*sp.scan(CASES / "vulnerable-app"))
    assert "NOT confirmed vulnerabilities" in text and "false positives" in text

def test_clean_fixture_has_no_findings_and_has_lockfile():
    inv, findings = sp.scan(CASES / "clean-app")
    assert findings == []
    assert inv["missing_lockfiles"] == [] and inv["lockfiles"]

def test_generated_dirs_skipped_by_default_and_opt_in():
    _, findings = sp.scan(CASES / "ignored-dirs")
    assert findings == []
    _, findings = sp.scan(CASES / "ignored-dirs", include_generated=True)
    assert {"db-url-with-password", "debug-enabled"} <= rules(findings)

def test_secret_values_never_printed(tmp_path, capsys):
    aws = "AKIA" + "QWERTYUIOP123456"[:16]
    gh = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"
    (tmp_path / "config.py").write_text(f'AWS="{aws}"\nGH="{gh}"\nDB="postgres://u:Zk39xQ72pLm@h/db"\nKEY="-----BEGIN RSA PRIVATE KEY-----"\n')
    inv, findings = sp.scan(tmp_path)
    assert {"aws-access-key-id", "github-token", "db-url-with-password", "private-key-block"} <= rules(findings)
    text = sp.render_text(inv, findings)
    js = json.dumps([f.__dict__ for f in findings])
    for secret in (aws, gh, "Zk39xQ72pLm"):
        assert secret not in text and secret not in js
    assert "[REDACTED len=" in text
    rc = sp.main([str(tmp_path), "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0 and aws not in out and gh not in out and "Zk39xQ72pLm" not in out

def test_placeholder_is_low_confidence_false_positive(tmp_path):
    (tmp_path / "settings.py").write_text('API_KEY = "your-api-key-here"\nTOKEN = "<insert-token-here>"\n')
    _, findings = sp.scan(tmp_path)
    assert findings and all(f.confidence == "low" for f in findings)
    assert all("placeholder" in f.note for f in findings)

def test_example_env_not_flagged_as_env_file(tmp_path):
    (tmp_path / ".env.example").write_text("DATABASE_URL=\n")
    _, findings = sp.scan(tmp_path)
    assert "env-file-present" not in rules(findings)

def test_env_file_in_public_dir_and_gitignore_awareness(tmp_path):
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / ".env").write_text("X=1\n")
    _, findings = sp.scan(tmp_path)
    f = next(x for x in findings if x.rule == "env-file-present")
    assert f.confidence == "medium" and "publicly" in f.note
    (tmp_path / ".gitignore").write_text(".env*\n")
    (tmp_path / "private").mkdir()
    (tmp_path / "private" / ".env").write_text("X=1\n")
    _, findings = sp.scan(tmp_path)
    priv = next(x for x in findings if x.file.startswith("private"))
    assert priv.confidence == "low"

def test_target_not_modified(tmp_path):
    import shutil
    dst = tmp_path / "copy"
    shutil.copytree(CASES / "vulnerable-app", dst)
    before = tree_hash(dst)
    sp.scan(dst)
    sp.main([str(dst)])
    assert tree_hash(dst) == before

def test_invalid_target_path(tmp_path, capsys):
    assert sp.main([str(tmp_path / "nope")]) == 2
    f = tmp_path / "file.txt"; f.write_text("x")
    assert sp.main([str(f)]) == 2

def test_output_inside_target_refused(tmp_path):
    (tmp_path / "a.py").write_text("x=1\n")
    assert sp.main([str(tmp_path), "--output", str(tmp_path / "report.txt")]) == 2
    assert not (tmp_path / "report.txt").exists()

def test_output_outside_target_written(tmp_path):
    t = tmp_path / "t"; t.mkdir(); (t / "a.py").write_text("DEBUG = True\n")
    out = tmp_path / "report.json"
    assert sp.main([str(t), "--format", "json", "--output", str(out)]) == 0
    assert json.loads(out.read_text())["findings"]

def test_unreadable_and_binary_and_symlink_handled(tmp_path, monkeypatch):
    (tmp_path / "bin.dat").write_bytes(b"\x00\x01DEBUG = True")
    (tmp_path / "ok.py").write_text("DEBUG = True\n")
    (tmp_path / "broken").symlink_to(tmp_path / "missing-target")
    (tmp_path / "locked.py").write_text("DEBUG = True\n")
    real_open = open
    def fake_open(p, *a, **k):
        if str(p).endswith("locked.py"):
            raise PermissionError("denied")
        return real_open(p, *a, **k)
    monkeypatch.setattr("builtins.open", fake_open)
    inv, findings = sp.scan(tmp_path)
    reasons = {s["file"]: s["reason"] for s in inv["files_skipped"]}
    assert reasons["bin.dat"] == "binary"
    assert "symlink" in reasons["broken"]
    assert "unreadable" in reasons["locked.py"]
    assert any(f.file == "ok.py" for f in findings)

def test_large_file_skipped(tmp_path):
    (tmp_path / "big.txt").write_text("x" * (sp.MAX_FILE_BYTES + 1))
    inv, _ = sp.scan(tmp_path)
    assert any(s["reason"].startswith("larger") for s in inv["files_skipped"])

def test_test_paths_downgraded(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "t.py").write_text('DB="postgres://u:Zk39xQ72pLm@h/db"\n')
    _, findings = sp.scan(tmp_path)
    assert findings and all(f.confidence == "low" and "fixture" in f.note for f in findings)

def test_fail_on_findings_exit_code():
    assert sp.main([str(CASES / "vulnerable-app"), "--fail-on-findings"]) == 1
    assert sp.main([str(CASES / "clean-app"), "--fail-on-findings"]) == 0

def test_no_network_imports():
    import re
    src = (ROOT / "scripts" / "scan_project.py").read_text()
    assert not re.search(r"^\s*(?:import|from)\s+(?:urllib|requests|socket|http|ftplib|smtplib)", src, re.M)
