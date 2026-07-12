from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests.support import SKILL_ROOT
from contracts import (
    ContractError,
    load_json,
    normalize_terms,
    safe_relative_path,
    validate_compliance_report,
    validate_conflict_report,
    validate_design_rule_bundle,
    validate_selection_profile,
    write_json,
)


SCHEMA_VERSIONS = {
    "selection-profile": "ui-design-system-selection-profile/v1",
    "design-rule-bundle": "ui-design-system-design-rule-bundle/v1",
    "conflict-report": "ui-design-system-conflict-report/v1",
    "compliance-report": "ui-design-system-compliance-report/v1",
}

REQUIRED_FIELDS = {
    "selection-profile": {
        "schemaVersion",
        "taskMode",
        "brief",
        "industry",
        "audience",
        "productType",
        "tone",
        "theme",
        "density",
        "layoutNeeds",
        "contentNeeds",
        "componentNeeds",
        "requiredTraits",
        "excludedTraits",
        "inputSources",
        "explicitSystem",
    },
    "design-rule-bundle": {
        "schemaVersion",
        "system",
        "files",
        "tokens",
        "rules",
        "warnings",
        "approvedDeviations",
    },
    "conflict-report": {
        "schemaVersion",
        "system",
        "conflicts",
        "alternatives",
        "decisions",
        "status",
    },
    "compliance-report": {
        "schemaVersion",
        "status",
        "system",
        "machineChecks",
        "agentReviews",
        "findings",
        "diffSummary",
    },
}


def selection_profile():
    return {
        "schemaVersion": SCHEMA_VERSIONS["selection-profile"],
        "taskMode": "new-design",
        "brief": "Create a calm analytics dashboard.",
        "industry": ["backend-data"],
        "audience": ["technical-operators"],
        "productType": ["analytics-dashboard"],
        "tone": ["calm"],
        "theme": ["dark"],
        "density": ["compact"],
        "layoutNeeds": ["dashboard-grid"],
        "contentNeeds": ["data-visualization"],
        "componentNeeds": ["tables"],
        "requiredTraits": [],
        "excludedTraits": [],
        "inputSources": [],
        "explicitSystem": None,
    }


def design_rule_bundle():
    return {
        "schemaVersion": SCHEMA_VERSIONS["design-rule-bundle"],
        "system": {"id": "minimal", "name": "Minimal", "assetVersion": "2026-07-12"},
        "files": ["manifest.json", "tokens.css"],
        "tokens": [{"name": "--color-bg", "value": "#ffffff", "source": "tokens.css"}],
        "rules": [
            {
                "id": "color-background",
                "category": "color",
                "scope": ["page"],
                "enforcement": "machine-enforced",
                "evidence": "Use the background token.",
                "source": "DESIGN.md",
                "location": {"line": 12},
                "confidence": 1.0,
                "warnings": [],
            }
        ],
        "warnings": [],
        "approvedDeviations": [],
    }


def conflict_report():
    return {
        "schemaVersion": SCHEMA_VERSIONS["conflict-report"],
        "system": {"id": "minimal", "name": "Minimal", "assetVersion": "2026-07-12"},
        "conflicts": [
            {
                "requirement": "Use a decorative animated background.",
                "rule": {"id": "motion-restraint", "summary": "Avoid decorative motion."},
                "risks": {
                    "visual": "Conflicts with the restrained visual language.",
                    "usability": "May distract from primary content.",
                    "brand": "Weakens the selected system identity.",
                    "implementation": "Adds unnecessary animation code.",
                },
            }
        ],
        "alternatives": [{"systemId": "playful", "reason": "Supports expressive motion."}],
        "decisions": ["switch-system", "keep-current-system", "adjust-requirements", "other"],
        "status": "awaiting-user-decision",
    }


def compliance_report():
    return {
        "schemaVersion": SCHEMA_VERSIONS["compliance-report"],
        "status": "review-required",
        "system": {"id": "minimal", "name": "Minimal", "assetVersion": "2026-07-12"},
        "machineChecks": [{"name": "raw-color-scan", "status": "verified"}],
        "agentReviews": [{"name": "visual-review", "status": "agent-judgment"}],
        "findings": [
            {
                "severity": "high",
                "ruleId": "color-background",
                "evidence": "styles.css:12 uses #ffffff directly.",
                "reason": "The selected system requires a token reference.",
                "recommendation": "Replace the raw color with var(--color-bg).",
                "confidence": 1.0,
                "verificationStatus": "verified",
            }
        ],
        "diffSummary": {"before": "One issue found.", "after": None, "modified": False},
    }


class ContractTests(unittest.TestCase):
    def test_safe_relative_path_rejects_escape(self):
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(ContractError):
                safe_relative_path(Path(temp_dir), "../outside.json")

    def test_safe_relative_path_rejects_absolute_path(self):
        with TemporaryDirectory() as temp_dir:
            absolute_path = Path(temp_dir) / "inside.json"
            with self.assertRaisesRegex(ContractError, r"\$"):
                safe_relative_path(Path(temp_dir), absolute_path)

    def test_safe_relative_path_rejects_any_parent_segment(self):
        with TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ContractError, r"\$"):
                safe_relative_path(Path(temp_dir), "nested/../inside.json")

    def test_safe_relative_path_returns_resolved_path_inside_root(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.assertEqual(
                safe_relative_path(root, "nested/contract.json"),
                (root / "nested" / "contract.json").resolve(),
            )

    def test_normalize_terms_is_stable(self):
        self.assertEqual(normalize_terms(["Dark Mode", "dark-mode", "  SaaS  "]), ["dark-mode", "saas"])

    def test_normalize_terms_normalizes_separators_and_deduplicates_in_input_order(self):
        values = ["Design_System", "design system", "DESIGN--SYSTEM", "Data Dense", ""]
        self.assertEqual(normalize_terms(values), ["design-system", "data-dense"])

    def test_normalize_terms_reports_the_invalid_item_path(self):
        with self.assertRaisesRegex(ContractError, r"\$\[1\]"):
            normalize_terms(["valid", 3])

    def test_json_round_trip_is_utf8_sorted_indented_and_has_one_trailing_newline(self):
        value = {"zeta": [1, 2], "message": "你好，设计系统"}
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "nested" / "contract.json"
            write_json(path, value)
            raw = path.read_bytes()
            text = raw.decode("utf-8")

            self.assertEqual(load_json(path), value)
            self.assertIn("你好，设计系统".encode("utf-8"), raw)
            self.assertLess(text.index('"message"'), text.index('"zeta"'))
            self.assertIn("\n  \"message\"", text)
            self.assertTrue(text.endswith("\n"))
            self.assertFalse(text.endswith("\n\n"))

    def test_load_json_wraps_parse_and_io_errors(self):
        with TemporaryDirectory() as temp_dir:
            invalid_path = Path(temp_dir) / "invalid.json"
            invalid_path.write_text("{", encoding="utf-8")
            for path in (invalid_path, Path(temp_dir) / "missing.json"):
                with self.subTest(path=path.name):
                    with self.assertRaisesRegex(ContractError, r"\$"):
                        load_json(path)

    def test_selection_profile_requires_mode_and_brief(self):
        with self.assertRaises(ContractError):
            validate_selection_profile({"taskMode": "audit"})

    def test_selection_profile_reports_missing_required_field_path(self):
        value = selection_profile()
        del value["brief"]
        with self.assertRaisesRegex(ContractError, r"\$\.brief"):
            validate_selection_profile(value)

    def test_selection_profile_rejects_invalid_task_mode(self):
        value = selection_profile()
        value["taskMode"] = "repair"
        with self.assertRaisesRegex(ContractError, r"\$\.taskMode"):
            validate_selection_profile(value)

    def test_selection_profile_accepts_all_task_modes(self):
        for task_mode in ("new-design", "redesign", "audit"):
            with self.subTest(task_mode=task_mode):
                value = selection_profile()
                value["taskMode"] = task_mode
                self.assertIs(validate_selection_profile(value), value)

    def test_selection_profile_accepts_nonempty_input_sources_with_access_status(self):
        value = selection_profile()
        value["inputSources"] = [
            {
                "kind": "url",
                "value": "https://example.com/dashboard",
                "accessStatus": "accessible",
            }
        ]
        self.assertIs(validate_selection_profile(value), value)

    def test_selection_profile_schema_models_input_sources_as_objects(self):
        schema = load_json(SKILL_ROOT / "schemas" / "selection-profile.schema.json")
        self.assertEqual(schema["properties"]["inputSources"]["items"]["type"], "object")

    def test_design_rule_bundle_rejects_invalid_enforcement(self):
        value = design_rule_bundle()
        value["rules"][0]["enforcement"] = "automatic"
        with self.assertRaisesRegex(ContractError, r"\$\.rules\[0\]\.enforcement"):
            validate_design_rule_bundle(value)

    def test_conflict_report_rejects_invalid_status(self):
        value = conflict_report()
        value["status"] = "continue"
        with self.assertRaisesRegex(ContractError, r"\$\.status"):
            validate_conflict_report(value)

    def test_conflict_report_rejects_invalid_decision(self):
        value = conflict_report()
        value["decisions"][0] = "auto-select"
        with self.assertRaisesRegex(ContractError, r"\$\.decisions\[0\]"):
            validate_conflict_report(value)

    def test_compliance_report_rejects_invalid_report_status(self):
        value = compliance_report()
        value["status"] = "fixed-without-approval"
        with self.assertRaisesRegex(ContractError, r"\$\.status"):
            validate_compliance_report(value)

    def test_compliance_report_rejects_invalid_severity(self):
        value = compliance_report()
        value["findings"][0]["severity"] = "urgent"
        with self.assertRaisesRegex(ContractError, r"\$\.findings\[0\]\.severity"):
            validate_compliance_report(value)

    def test_compliance_report_rejects_invalid_verification_status(self):
        value = compliance_report()
        value["findings"][0]["verificationStatus"] = "assumed"
        with self.assertRaisesRegex(ContractError, r"\$\.findings\[0\]\.verificationStatus"):
            validate_compliance_report(value)

    def test_all_contracts_accept_valid_values(self):
        cases = (
            (validate_design_rule_bundle, design_rule_bundle()),
            (validate_conflict_report, conflict_report()),
            (validate_compliance_report, compliance_report()),
        )
        for validator, value in cases:
            with self.subTest(validator=validator.__name__):
                self.assertIs(validator(value), value)

    def test_all_contracts_reject_wrong_schema_version_with_field_path(self):
        cases = (
            (validate_selection_profile, selection_profile()),
            (validate_design_rule_bundle, design_rule_bundle()),
            (validate_conflict_report, conflict_report()),
            (validate_compliance_report, compliance_report()),
        )
        for validator, original in cases:
            with self.subTest(validator=validator.__name__):
                value = deepcopy(original)
                value["schemaVersion"] = "unsupported/v2"
                with self.assertRaisesRegex(ContractError, r"\$\.schemaVersion"):
                    validator(value)

    def test_schemas_declare_exact_version_required_fields_and_closed_top_level(self):
        for name, version in SCHEMA_VERSIONS.items():
            with self.subTest(schema=name):
                schema = load_json(SKILL_ROOT / "schemas" / f"{name}.schema.json")
                self.assertEqual(schema["properties"]["schemaVersion"]["const"], version)
                self.assertEqual(set(schema["required"]), REQUIRED_FIELDS[name])
                self.assertIs(schema["additionalProperties"], False)


if __name__ == "__main__":
    unittest.main()
