from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from tests.support import SCRIPTS_ROOT
from compile_rules import compile_rule_bundle, extract_markdown_rules, parse_root_tokens


CSS = """.card { --ignored: red; }
:root {
  --color-brand: #ffffff;
  --color-brand: #000000;
  --space-1: 4px;
}
"""

DESIGN = """# Fixture System

## Color Rules
- Must use the brand color token.
- Never mix unrelated accent colors.
- 禁止使用未声明的颜色。
- 不得隐藏键盘焦点。

Keep secondary surfaces visually quiet.
"""


def write_system(root: Path, include_usage: bool = False) -> Path:
    system = root / "fixture"
    system.mkdir()
    manifest = {
        "schemaVersion": "od-design-system-project/v1",
        "id": "fixture",
        "name": "Fixture",
        "category": "Starter",
        "description": "Compiler fixture.",
        "files": {"design": "DESIGN.md", "tokens": "tokens.css", "components": "components.html"},
        "usage": "USAGE.md",
    }
    (system / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (system / "tokens.css").write_text(CSS, encoding="utf-8")
    (system / "DESIGN.md").write_text(DESIGN, encoding="utf-8")
    (system / "components.html").write_text("<button>Action</button>\n", encoding="utf-8")
    if include_usage:
        (system / "USAGE.md").write_text("## Usage\n- Use tokens consistently.\n", encoding="utf-8")
    return system


class CompileRulesTests(unittest.TestCase):
    def test_root_token_parser_preserves_source_line_and_duplicates(self):
        tokens = parse_root_tokens(CSS, "tokens.css")
        self.assertEqual([token["name"] for token in tokens], ["--color-brand", "--color-brand", "--space-1"])
        self.assertEqual(tokens[0]["source"], "tokens.css")
        self.assertEqual(tokens[0]["location"]["line"], 3)
        self.assertEqual(tokens[1]["location"]["line"], 4)
        self.assertNotIn("--ignored", [token["name"] for token in tokens])

    def test_markdown_parser_preserves_raw_evidence_heading_and_line(self):
        rules = extract_markdown_rules(DESIGN, "DESIGN.md")
        must_rule = next(rule for rule in rules if rule["evidence"].startswith("Must use"))
        self.assertEqual(must_rule["source"], "DESIGN.md")
        self.assertEqual(must_rule["location"]["line"], 4)
        self.assertEqual(must_rule["location"]["heading"], "Color Rules")
        self.assertEqual(must_rule["category"], "color-rules")
        self.assertEqual(must_rule["scope"], ["color-rules"])

    def test_explicit_terms_are_classified_as_prohibitions(self):
        rules = extract_markdown_rules(DESIGN, "DESIGN.md")
        for marker in ("Must", "Never", "禁止", "不得"):
            with self.subTest(marker=marker):
                rule = next(item for item in rules if marker in item["evidence"])
                self.assertEqual(rule["enforcement"], "explicit-prohibition")
                self.assertGreaterEqual(rule["confidence"], 0.9)

    def test_compact_paragraph_is_preserved_as_provisional_rule(self):
        rules = extract_markdown_rules(DESIGN, "DESIGN.md")
        paragraph = next(rule for rule in rules if rule["evidence"].startswith("Keep secondary"))
        self.assertIn(paragraph["enforcement"], {"agent-review", "preference"})
        self.assertIn("provisional-natural-language-classification", paragraph["warnings"])

    def test_bundle_reports_duplicate_token_conflicts(self):
        with TemporaryDirectory() as temp_dir:
            bundle = compile_rule_bundle(write_system(Path(temp_dir)))
            self.assertTrue(any("--color-brand" in warning for warning in bundle["warnings"]))
            self.assertEqual(len([token for token in bundle["tokens"] if token["name"] == "--color-brand"]), 2)

    def test_missing_optional_usage_is_legal(self):
        with TemporaryDirectory() as temp_dir:
            bundle = compile_rule_bundle(write_system(Path(temp_dir), include_usage=False))
            self.assertEqual(bundle["system"]["id"], "fixture")
            self.assertNotIn("USAGE.md", bundle["files"])
            self.assertTrue(bundle["tokens"])
            self.assertTrue(bundle["rules"])
            self.assertIn("components.html", bundle["files"])

    def test_usage_rules_are_compiled_when_file_exists(self):
        with TemporaryDirectory() as temp_dir:
            bundle = compile_rule_bundle(write_system(Path(temp_dir), include_usage=True))
            self.assertIn("USAGE.md", bundle["files"])
            self.assertTrue(any(rule["source"] == "USAGE.md" for rule in bundle["rules"]))

    def test_compilation_is_deterministic_and_does_not_mutate_inputs(self):
        with TemporaryDirectory() as temp_dir:
            system = write_system(Path(temp_dir))
            before = {p.name: p.read_bytes() for p in system.iterdir() if p.is_file()}
            first = compile_rule_bundle(system)
            second = compile_rule_bundle(system)
            after = {p.name: p.read_bytes() for p in system.iterdir() if p.is_file()}
            self.assertEqual(first, second)
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
