from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests.support import REPO_ROOT, SKILL_ROOT, SCRIPTS_ROOT
from audit_static import scan_project
from build_catalog import build_inventory
from compile_rules import compile_rule_bundle
from contracts import (
    load_json,
    validate_compliance_report,
    validate_conflict_report,
    validate_design_rule_bundle,
    validate_selection_profile,
    write_json,
)
from recommend_systems import recommend
from validate_package import validate_package


PROFILE_PATH = REPO_ROOT / "tests" / "fixtures" / "selection-profile.json"
CATALOG_PATH = SKILL_ROOT / "assets" / "catalog" / "design-systems.index.json"
ASSET_ROOT = SKILL_ROOT / "assets" / "design-systems"
SAMPLE_UI = REPO_ROOT / "tests" / "fixtures" / "sample-ui"


class EndToEndTests(unittest.TestCase):
    def test_selection_compile_audit_and_contract_pipeline(self):
        profile = load_json(PROFILE_PATH)
        catalog = load_json(CATALOG_PATH)
        validate_selection_profile(profile)
        before = build_inventory(ASSET_ROOT)

        selection = recommend(profile, catalog)
        self.assertEqual(selection["status"], "awaiting-user-selection")
        self.assertTrue(selection["recommendations"])
        selected_id = selection["recommendations"][0]["id"]
        bundle = compile_rule_bundle(ASSET_ROOT / selected_id)
        validate_design_rule_bundle(bundle)
        report = scan_project(SAMPLE_UI, bundle)
        validate_compliance_report(report)

        with TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir)
            bundle_path = output_root / "bundle.json"
            report_path = output_root / "report.json"
            write_json(bundle_path, bundle)
            write_json(report_path, report)
            validate_design_rule_bundle(load_json(bundle_path))
            validate_compliance_report(load_json(report_path))

        alternative = selection["recommendations"][1] if len(selection["recommendations"]) > 1 else selection["recommendations"][0]
        conflict = {
            "schemaVersion": "ui-design-system-conflict-report/v1",
            "system": bundle["system"],
            "conflicts": [{
                "requirement": "Use an effect that conflicts with a reviewed rule.",
                "rule": {"id": bundle["rules"][0]["id"], "summary": bundle["rules"][0]["evidence"]},
                "risks": {"usability": "The conflict could reduce task clarity."},
            }],
            "alternatives": [{"systemId": alternative["id"], "reason": "A reliable catalog candidate."}],
            "decisions": ["switch-system", "keep-current-system", "adjust-requirements", "other"],
            "status": "awaiting-user-decision",
        }
        validate_conflict_report(conflict)
        self.assertFalse(report["diffSummary"]["modified"])
        self.assertEqual(validate_package(SKILL_ROOT, expected_system_count=151), [])
        self.assertEqual(build_inventory(ASSET_ROOT), before)

    def test_no_match_branch_stays_empty_and_exposes_preview(self):
        profile = deepcopy(load_json(PROFILE_PATH))
        profile["requiredTraits"] = ["trait-that-no-bundled-system-declares"]
        result = recommend(profile, load_json(CATALOG_PATH))
        self.assertEqual(result["status"], "awaiting-manual-selection")
        self.assertEqual(result["recommendations"], [])
        self.assertEqual(result["previewUrl"], "https://open-design.ai/zh/plugins/systems/")


if __name__ == "__main__":
    unittest.main()
