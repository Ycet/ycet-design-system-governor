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
    def assert_contract_path(self, validator, value, path):
        with self.assertRaises(ContractError) as caught:
            validator(value)
        self.assertIn(path, str(caught.exception))

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

    def test_selection_profile_rejects_non_string_task_mode_as_contract_error(self):
        value = selection_profile()
        value["taskMode"] = []
        self.assert_contract_path(validate_selection_profile, value, "$.taskMode")

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

    def test_input_source_requires_kind_value_and_access_status(self):
        source = {"kind": "url", "value": "https://example.com", "accessStatus": "accessible"}
        for field in ("kind", "value", "accessStatus"):
            with self.subTest(field=field):
                value = selection_profile()
                value["inputSources"] = [dict(source)]
                del value["inputSources"][0][field]
                self.assert_contract_path(validate_selection_profile, value, f"$.inputSources[0].{field}")

    def test_input_source_rejects_invalid_fields_with_exact_paths(self):
        cases = (
            ("kind", "video", "$.inputSources[0].kind"),
            ("value", "  ", "$.inputSources[0].value"),
            ("accessStatus", "pending", "$.inputSources[0].accessStatus"),
        )
        for field, invalid, path in cases:
            with self.subTest(field=field):
                value = selection_profile()
                value["inputSources"] = [
                    {"kind": "url", "value": "https://example.com", "accessStatus": "accessible"}
                ]
                value["inputSources"][0][field] = invalid
                self.assert_contract_path(validate_selection_profile, value, path)

    def test_enum_fields_reject_non_string_values_as_contract_errors(self):
        rule_bundle = design_rule_bundle()
        rule_bundle["rules"][0]["enforcement"] = []
        report = compliance_report()
        report["status"] = []
        finding_report = compliance_report()
        finding_report["findings"][0]["verificationStatus"] = []
        cases = (
            (validate_design_rule_bundle, rule_bundle, "$.rules[0].enforcement"),
            (validate_compliance_report, report, "$.status"),
            (validate_compliance_report, finding_report, "$.findings[0].verificationStatus"),
        )
        for validator, value, path in cases:
            with self.subTest(path=path):
                self.assert_contract_path(validator, value, path)

    def test_selection_profile_schema_models_input_sources_as_objects(self):
        schema = load_json(SKILL_ROOT / "schemas" / "selection-profile.schema.json")
        item = schema["properties"]["inputSources"]["items"]
        self.assertEqual(item["type"], "object")
        self.assertEqual(set(item["required"]), {"kind", "value", "accessStatus"})
        self.assertEqual(
            item["properties"]["kind"]["enum"],
            ["project", "code", "screenshot", "design-file", "url", "figma", "document", "other"],
        )
        self.assertEqual(
            item["properties"]["accessStatus"]["enum"],
            ["accessible", "degraded", "unavailable"],
        )
        self.assertIs(item["additionalProperties"], False)

    def test_design_rule_bundle_rejects_invalid_enforcement(self):
        value = design_rule_bundle()
        value["rules"][0]["enforcement"] = "automatic"
        with self.assertRaisesRegex(ContractError, r"\$\.rules\[0\]\.enforcement"):
            validate_design_rule_bundle(value)

    def test_design_rule_rejects_rule_with_only_enforcement(self):
        value = design_rule_bundle()
        value["rules"] = [{"enforcement": "machine-enforced"}]
        self.assert_contract_path(validate_design_rule_bundle, value, "$.rules[0].id")

    def test_design_rule_requires_every_rule_field(self):
        fields = (
            "id",
            "category",
            "scope",
            "enforcement",
            "evidence",
            "source",
            "location",
            "confidence",
            "warnings",
        )
        for field in fields:
            with self.subTest(field=field):
                value = design_rule_bundle()
                del value["rules"][0][field]
                self.assert_contract_path(validate_design_rule_bundle, value, f"$.rules[0].{field}")

    def test_design_rule_rejects_invalid_field_shapes(self):
        cases = (
            ("id", "", "$.rules[0].id"),
            ("category", "", "$.rules[0].category"),
            ("scope", [], "$.rules[0].scope"),
            ("scope", ["page", 3], "$.rules[0].scope[1]"),
            ("evidence", "", "$.rules[0].evidence"),
            ("location", [], "$.rules[0].location"),
            ("warnings", {}, "$.rules[0].warnings"),
        )
        for field, invalid, path in cases:
            with self.subTest(field=field, invalid=invalid):
                value = design_rule_bundle()
                value["rules"][0][field] = invalid
                self.assert_contract_path(validate_design_rule_bundle, value, path)

    def test_design_rule_rejects_bad_confidence(self):
        for confidence in (True, -0.1, 1.1):
            with self.subTest(confidence=confidence):
                value = design_rule_bundle()
                value["rules"][0]["confidence"] = confidence
                self.assert_contract_path(validate_design_rule_bundle, value, "$.rules[0].confidence")

    def test_design_rule_rejects_unsafe_source(self):
        value = design_rule_bundle()
        value["rules"][0]["source"] = "../DESIGN.md"
        self.assert_contract_path(validate_design_rule_bundle, value, "$.rules[0].source")

    def test_design_rule_rejects_duplicate_rule_id(self):
        value = design_rule_bundle()
        value["rules"].append(deepcopy(value["rules"][0]))
        self.assert_contract_path(validate_design_rule_bundle, value, "$.rules[1].id")

    def test_design_rule_schema_declares_complete_closed_rule_contract(self):
        schema = load_json(SKILL_ROOT / "schemas" / "design-rule-bundle.schema.json")
        item = schema["properties"]["rules"]["items"]
        self.assertEqual(
            set(item["required"]),
            {"id", "category", "scope", "enforcement", "evidence", "source", "location", "confidence", "warnings"},
        )
        self.assertIs(item["additionalProperties"], False)
        self.assertEqual(item["properties"]["scope"]["minItems"], 1)
        self.assertEqual(item["properties"]["confidence"]["minimum"], 0)
        self.assertEqual(item["properties"]["confidence"]["maximum"], 1)
        self.assertIn("pattern", item["properties"]["source"])

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

    def test_conflict_report_requires_nonempty_collections(self):
        for field in ("conflicts", "alternatives", "decisions"):
            with self.subTest(field=field):
                value = conflict_report()
                value[field] = []
                self.assert_contract_path(validate_conflict_report, value, f"$.{field}")

    def test_conflict_report_requires_nested_fields(self):
        for field in ("requirement", "rule", "risks"):
            with self.subTest(container="conflict", field=field):
                value = conflict_report()
                del value["conflicts"][0][field]
                self.assert_contract_path(validate_conflict_report, value, f"$.conflicts[0].{field}")
        for field in ("id", "summary"):
            with self.subTest(container="rule", field=field):
                value = conflict_report()
                del value["conflicts"][0]["rule"][field]
                self.assert_contract_path(validate_conflict_report, value, f"$.conflicts[0].rule.{field}")
        for field in ("systemId", "reason"):
            with self.subTest(container="alternative", field=field):
                value = conflict_report()
                del value["alternatives"][0][field]
                self.assert_contract_path(validate_conflict_report, value, f"$.alternatives[0].{field}")

    def test_conflict_report_rejects_invalid_risks(self):
        cases = (
            ({}, "$.conflicts[0].risks"),
            ({"security": "Unknown category."}, "$.conflicts[0].risks.security"),
            ({"visual": ""}, "$.conflicts[0].risks.visual"),
            ([], "$.conflicts[0].risks"),
        )
        for risks, path in cases:
            with self.subTest(risks=risks):
                value = conflict_report()
                value["conflicts"][0]["risks"] = risks
                self.assert_contract_path(validate_conflict_report, value, path)

    def test_conflict_report_requires_complete_unique_decision_set(self):
        cases = (
            (["switch-system", "keep-current-system", "adjust-requirements"], "incomplete"),
            (["switch-system", "keep-current-system", "adjust-requirements", "switch-system"], "duplicate"),
        )
        for decisions, label in cases:
            with self.subTest(label=label):
                value = conflict_report()
                value["decisions"] = decisions
                self.assert_contract_path(validate_conflict_report, value, "$.decisions")

    def test_conflict_schema_declares_nested_and_nonempty_contracts(self):
        schema = load_json(SKILL_ROOT / "schemas" / "conflict-report.schema.json")
        conflicts = schema["properties"]["conflicts"]
        alternatives = schema["properties"]["alternatives"]
        decisions = schema["properties"]["decisions"]
        self.assertEqual(conflicts["minItems"], 1)
        self.assertEqual(set(conflicts["items"]["required"]), {"requirement", "rule", "risks"})
        self.assertIs(conflicts["items"]["additionalProperties"], False)
        self.assertEqual(conflicts["items"]["properties"]["risks"]["minProperties"], 1)
        self.assertIs(conflicts["items"]["properties"]["risks"]["additionalProperties"], False)
        self.assertEqual(alternatives["minItems"], 1)
        self.assertEqual(set(alternatives["items"]["required"]), {"systemId", "reason"})
        self.assertEqual(decisions["minItems"], 4)
        self.assertEqual(decisions["maxItems"], 4)
        self.assertIs(decisions["uniqueItems"], True)

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

    def test_compliance_finding_rejects_object_with_only_two_fields(self):
        value = compliance_report()
        value["findings"] = [{"severity": "high", "ruleId": "color-background"}]
        self.assert_contract_path(validate_compliance_report, value, "$.findings[0].evidence")

    def test_compliance_finding_requires_every_field(self):
        fields = (
            "severity",
            "ruleId",
            "evidence",
            "reason",
            "recommendation",
            "confidence",
            "verificationStatus",
        )
        for field in fields:
            with self.subTest(field=field):
                value = compliance_report()
                del value["findings"][0][field]
                self.assert_contract_path(validate_compliance_report, value, f"$.findings[0].{field}")

    def test_compliance_finding_rejects_empty_strings(self):
        for field in ("ruleId", "evidence", "reason", "recommendation"):
            with self.subTest(field=field):
                value = compliance_report()
                value["findings"][0][field] = ""
                self.assert_contract_path(validate_compliance_report, value, f"$.findings[0].{field}")

    def test_compliance_finding_rejects_bad_confidence(self):
        for confidence in (True, -0.1, 1.1):
            with self.subTest(confidence=confidence):
                value = compliance_report()
                value["findings"][0]["confidence"] = confidence
                self.assert_contract_path(validate_compliance_report, value, "$.findings[0].confidence")

    def test_compliance_checks_and_reviews_require_name_and_verification_status(self):
        for field in ("machineChecks", "agentReviews"):
            for required in ("name", "status"):
                with self.subTest(field=field, required=required):
                    value = compliance_report()
                    del value[field][0][required]
                    self.assert_contract_path(validate_compliance_report, value, f"$.{field}[0].{required}")
            with self.subTest(field=field, status="invalid"):
                value = compliance_report()
                value[field][0]["status"] = "passed"
                self.assert_contract_path(validate_compliance_report, value, f"$.{field}[0].status")

    def test_compliance_diff_summary_requires_valid_fields(self):
        for field in ("before", "after", "modified"):
            with self.subTest(missing=field):
                value = compliance_report()
                del value["diffSummary"][field]
                self.assert_contract_path(validate_compliance_report, value, f"$.diffSummary.{field}")
        cases = (
            ("before", "", "$.diffSummary.before"),
            ("after", 3, "$.diffSummary.after"),
            ("modified", 1, "$.diffSummary.modified"),
        )
        for field, invalid, path in cases:
            with self.subTest(field=field, invalid=invalid):
                value = compliance_report()
                value["diffSummary"][field] = invalid
                self.assert_contract_path(validate_compliance_report, value, path)

    def test_compliance_review_required_cannot_claim_modification(self):
        value = compliance_report()
        value["diffSummary"]["modified"] = True
        self.assert_contract_path(validate_compliance_report, value, "$.diffSummary.modified")

    def test_compliance_schema_declares_nested_contracts(self):
        schema = load_json(SKILL_ROOT / "schemas" / "compliance-report.schema.json")
        properties = schema["properties"]
        finding = properties["findings"]["items"]
        expected_finding = {
            "severity",
            "ruleId",
            "evidence",
            "reason",
            "recommendation",
            "confidence",
            "verificationStatus",
        }
        self.assertEqual(set(finding["required"]), expected_finding)
        self.assertIs(finding["additionalProperties"], False)
        self.assertEqual(finding["properties"]["confidence"]["minimum"], 0)
        self.assertEqual(finding["properties"]["confidence"]["maximum"], 1)
        for field in ("machineChecks", "agentReviews"):
            self.assertEqual(set(properties[field]["items"]["required"]), {"name", "status"})
            self.assertIs(properties[field]["items"]["additionalProperties"], False)
        self.assertEqual(set(properties["diffSummary"]["required"]), {"before", "after", "modified"})
        self.assertIs(properties["diffSummary"]["additionalProperties"], False)

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
