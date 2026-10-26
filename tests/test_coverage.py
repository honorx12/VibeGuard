import json
from pathlib import Path

import validate_skills as vs

ROOT = Path(__file__).resolve().parent.parent
COV = json.loads((ROOT / "registry" / "coverage.json").read_text())

# Canonical lists copied from the project brief; independent of the generator data.
SECURITY = """Exposed database credentials|Public .env files|Hardcoded secrets|Weak authentication|Missing authorization checks|Cross-user access|Open database permissions|Cloud service misconfiguration|Unprotected admin routes|Exposed production debug tools|Secrets in logs|Verbose production errors|Secrets in Git history|Secrets in frontend JavaScript|Client-only security|Missing or weak input validation|SQL injection|NoSQL injection|Cross-site scripting (XSS)|Cross-site request forgery (CSRF)|Insecure file uploads|Path traversal|Server-side request forgery (SSRF)|Broken password reset flows|Weak session management|Exposed or weak JWT secrets and validation|Permissive CORS|Missing or ineffective rate limits|Exposed development and staging environments|Default credentials|Unsigned webhooks|Frontend-only payment verification|IDOR / BOLA|Unsafe APIs accepting untrusted input|Exposed logs|Exposed source maps|Vulnerable dependencies|Malicious packages|Prompt injection|Unpermissioned AI access|Excessive database permissions|Missing audit logs|Missing security monitoring|Missing or untested backups|Exposed internal dashboards|Missing security headers|Insecure cookie settings|Unencrypted sensitive data|Poor tenant isolation|Unreviewed code|Mass assignment|Command injection|Insecure deserialization|Misconfigured OAuth|Missing MFA|Account enumeration|Business logic abuse|Race conditions|Webhook replay|Insecure CI/CD|Untrusted build actions|Unpinned build dependencies|Security checks that fail open|Missing timeouts|Sensitive information leakage|Invalid AI output|Excessive AI permissions|Sensitive browser storage|Open redirects|Unsecured endpoints""".split("|")
UX = """Dark mode toggle|Cookie banner and preferences|Site search|Back-to-top button|Mobile navigation|Loading animations and skeleton states|Hover and focus states|Scroll progress bar|Copy-to-clipboard button|Print stylesheet|Sticky headers|Skip-to-content link|Password visibility toggle|UTM tracking|Form success states|Form error states|Confirmation dialogs|Accurate last-updated date|Expandable FAQ|Floating contact action""".split("|")
PROD = """Privacy policy|Terms and conditions|Remove frontend secrets|Enforce HTTPS|Cookie consent where applicable|Meta titles and descriptions|Social preview image|Favicon|Sitemap and robots.txt|Image alt text|Image compression|Page-load performance checks|Color contrast|Mobile responsiveness|Custom 404 page|Broken-link checks|Form validation|Spam protection|Analytics configuration|Clear primary call to action""".split("|")

def test_canonical_list_sizes():
    assert (len(SECURITY), len(UX), len(PROD)) == (70, 20, 20)

def test_security_items_match_brief_in_order():
    assert [i["title"] for i in COV["security"]] == SECURITY
    assert [i["id"] for i in COV["security"]] == [f"SEC-{n:02d}" for n in range(1, 71)]

def test_ux_items_match_brief_in_order():
    assert [i["title"] for i in COV["ux"]] == UX
    assert [i["id"] for i in COV["ux"]] == [f"UX-{n:02d}" for n in range(1, 21)]

def test_production_checklist_complete_plus_extensions():
    assert [i["title"] for i in COV["production"][:20]] == PROD
    assert len(COV["production"]) == 27

def test_every_item_has_skill_and_verification():
    for group in COV.values():
        for it in group:
            assert it["verification"].strip(), it["id"]
            assert it["primary_skill"], it["id"]

def test_coverage_validator_passes():
    assert vs.validate_coverage(ROOT / "registry" / "coverage.json", ROOT / "skills") == []

def test_each_id_documented_in_primary_skill_file():
    texts = {p.parent.name: p.read_text() for p in vs.find_skill_files(ROOT / "skills")}
    for group in COV.values():
        for it in group:
            assert f"### {it['id']} " in texts[it["primary_skill"]], it["id"]

def test_validator_detects_missing_item(tmp_path):
    import shutil
    shutil.copytree(ROOT / "skills", tmp_path / "skills")
    cov = json.loads(json.dumps(COV))
    cov["security"].pop()
    p = tmp_path / "cov.json"
    p.write_text(json.dumps(cov))
    assert any("expected 70" in e for e in vs.validate_coverage(p, tmp_path / "skills"))

def test_validator_detects_unknown_skill(tmp_path):
    cov = json.loads(json.dumps(COV))
    cov["ux"][0]["primary_skill"] = "ghost"
    p = tmp_path / "cov.json"
    p.write_text(json.dumps(cov))
    assert any("ghost" in e for e in vs.validate_coverage(p, ROOT / "skills"))

def test_coverage_map_document_lists_all_ids():
    md = (ROOT / "docs" / "COVERAGE_MAP.md").read_text()
    for group in COV.values():
        for it in group:
            assert f"| {it['id']} |" in md

def test_readme_counts_match_reality():
    n = len(vs.find_skill_files(ROOT / "skills"))
    assert f"{n} skills" in (ROOT / "README.md").read_text()
