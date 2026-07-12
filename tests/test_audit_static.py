from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests.support import REPO_ROOT, SCRIPTS_ROOT
from audit_static import scan_project


FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "sample-ui"


def bundle():
    return {
        "schemaVersion": "ui-design-system-design-rule-bundle/v1",
        "system": {"id": "fixture", "name": "Fixture", "assetVersion": "sha256:test"},
        "files": ["manifest.json", "DESIGN.md", "tokens.css"],
        "tokens": [
            {"name": "--known-token", "value": "#ffffff", "source": "tokens.css"},
            {"name": "--required-token", "value": "8px", "source": "tokens.css", "required": True},
        ],
        "rules": [],
        "warnings": [],
        "approvedDeviations": [],
    }


class AuditStaticTests(unittest.TestCase):
    def test_reports_raw_color_unknown_and_missing_required_token(self):
        report = scan_project(FIXTURE_ROOT, bundle())
        codes = [finding["ruleId"] for finding in report["findings"]]
        self.assertIn("raw-color", codes)
        self.assertIn("unknown-token", codes)
        self.assertIn("missing-required-token", codes)

    def test_evidence_uses_posix_relative_paths_and_one_based_lines(self):
        report = scan_project(FIXTURE_ROOT, bundle())
        raw = next(item for item in report["findings"] if item["ruleId"] == "raw-color")
        unknown = next(item for item in report["findings"] if item["ruleId"] == "unknown-token")
        self.assertTrue(raw["evidence"].startswith("styles.css:5:"), raw["evidence"])
        self.assertTrue(unknown["evidence"].startswith("styles.css:2:"), unknown["evidence"])
        self.assertNotIn("\\", raw["evidence"])

    def test_severity_and_review_gate_are_stable(self):
        report = scan_project(FIXTURE_ROOT, bundle())
        severities = {item["ruleId"]: item["severity"] for item in report["findings"]}
        self.assertEqual(severities["unknown-token"], "high")
        self.assertEqual(severities["missing-required-token"], "high")
        self.assertEqual(severities["raw-color"], "medium")
        self.assertEqual(report["status"], "review-required")
        self.assertEqual(report["diffSummary"]["after"], None)
        self.assertIs(report["diffSummary"]["modified"], False)

    def test_skips_excluded_directories_large_files_and_binary_extensions(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "ok.css").write_text("a { color: var(--unknown); }\n", encoding="utf-8")
            for directory in (".git", "node_modules", "dist", "build", ".next"):
                target = root / directory
                target.mkdir()
                (target / "ignored.css").write_text("a { color: var(--ignored); }\n", encoding="utf-8")
            (root / "large.css").write_bytes(b"a" * (2 * 1024 * 1024 + 1) + b"var(--large)")
            (root / "image.png").write_bytes(b"var(--binary)")
            report = scan_project(root, bundle())
            evidence = "\n".join(item["evidence"] for item in report["findings"])
            self.assertIn("src/ok.css", evidence)
            for marker in ("ignored.css", "large.css", "image.png", "--ignored", "--large", "--binary"):
                self.assertNotIn(marker, evidence)

    def test_invalid_utf8_source_produces_unreadable_finding_without_execution(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "broken.css").write_bytes(b"\xff\xfevar(--unknown)")
            report = scan_project(root, bundle())
            unreadable = next(item for item in report["findings"] if item["ruleId"] == "unreadable-file")
            self.assertTrue(unreadable["evidence"].startswith("broken.css:1:"))
            self.assertFalse(any(item["ruleId"] == "unknown-token" for item in report["findings"]))

    def test_scan_is_deterministic_and_does_not_modify_fixture(self):
        before = {p.relative_to(FIXTURE_ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in FIXTURE_ROOT.rglob("*") if p.is_file()}
        first = scan_project(FIXTURE_ROOT, bundle())
        second = scan_project(FIXTURE_ROOT, bundle())
        after = {p.relative_to(FIXTURE_ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in FIXTURE_ROOT.rglob("*") if p.is_file()}
        self.assertEqual(first, second)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
